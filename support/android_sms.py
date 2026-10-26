"""Read new, matching bank SMS locally through an authorized Android device."""
import os
import re
import shlex
import subprocess
import time


class AndroidSmsOtp:
    def __init__(self, adb=None, serial=None, timeout=45, *, marker=None, sender=None,
                 code_label='code'):
        self.adb = adb or os.getenv('ADB_PATH', r'C:\platform-tools\adb.exe')
        self.serial = serial or os.getenv('ANDROID_SERIAL')
        self.timeout = timeout
        self.marker = marker if marker is not None else os.getenv('BANK_SMS_MARKER', 'კოდის შეყვანით ადასტურებთ')
        self.sender = sender if sender is not None else os.getenv('BANK_SMS_SENDER', '')
        self.code_label = code_label
        if not code_label.strip():
            raise ValueError('The SMS code label must not be empty.')
        if not self.marker.strip():
            raise ValueError('BANK_SMS_MARKER must not be empty.')
        self.watermark = None

    def _run(self, args):
        command = [self.adb] + (['-s', self.serial] if self.serial else ['-d']) + args
        try:
            result = subprocess.run(command, capture_output=True, text=True,
                                    encoding='utf-8', errors='replace', timeout=15)
        except (OSError, subprocess.TimeoutExpired):
            raise RuntimeError('Android connection failed. Check ADB and the authorized phone.') from None
        output = result.stdout
        error = result.stderr
        if result.returncode or any(token in output + error for token in
                ('SecurityException', 'Permission Denial', 'Error while accessing', 'java.lang.')):
            raise RuntimeError('Android SMS access failed. No permission changes were attempted.')
        return output

    def _query(self, after=None):
        # Quote SQL literals and the remote shell independently.
        marker = self.marker.replace("'", "''").replace('%', r'\%').replace('_', r'\_')
        where = "body LIKE '%" + marker + "%' ESCAPE '\\'"
        if self.sender:
            where += " AND address='" + self.sender.replace("'", "''") + "'"
        if after is not None:
            where += f' AND _id > {int(after)}'
        remote = shlex.join(['content', 'query', '--uri', 'content://sms/inbox',
                             '--projection', '_id' if after is None else '_id:body', '--where', where])
        output = self._run(['shell', remote])
        rows = []
        for row in re.split(r'(?m)^Row: \d+ ', output):
            match = re.match(r'_id=(\d+)(?:, body=([\s\S]*))?\s*$', row)
            if match:
                rows.append((int(match[1]), match[2] or ''))
        return rows

    def arm(self):
        """Call BEFORE requesting the SMS; ignore every message already on the phone."""
        self.watermark = max((row_id for row_id, _ in self._query()), default=0)
        return self

    def wait_for_code(self, length=4):
        if self.watermark is None:
            raise RuntimeError('Call arm() before triggering the SMS request.')
        deadline = time.monotonic() + self.timeout
        if not isinstance(length, int) or not 4 <= length <= 8:
            raise ValueError('Unsupported OTP length.')
        pattern = re.compile(r'(?<!\w)' + re.escape(self.code_label)
                             + r'\s*[:;]\s*([0-9]{' + str(length) + r'})(?![0-9])', re.I)
        while time.monotonic() < deadline:
            candidates = []
            for row_id, body in self._query(self.watermark):
                if row_id <= self.watermark:
                    continue
                codes = pattern.findall(body)
                if len(codes) == 1:
                    candidates.append((row_id, codes[0]))
            if candidates:
                row_id, code = max(candidates)
                self.watermark = row_id
                return code
            time.sleep(1)
        raise TimeoutError('No new matching bank SMS with a valid code arrived in time.')
