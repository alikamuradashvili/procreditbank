import pytest

from support.android_sms import AndroidSmsOtp
from support.scenario import Bank, EndPoint, Scenario


@pytest.mark.parametrize('label,length,body', [
    ('code', 6, 'Example code ; 123456'),
    ('ერთჯერადი კოდი', 4, 'ერთჯერადი კოდი: 1234 company example'),
])
def test_only_new_matching_code_is_consumed(monkeypatch, label, length, body):
    reader = AndroidSmsOtp(marker='test marker', sender='', code_label=label)
    monkeypatch.setattr(reader, '_query', lambda after=None:
                        [(10, '')] if after is None else [(9, body), (11, body)])
    reader.arm()
    assert reader.wait_for_code(length) == '123456'[:length]
    assert reader.watermark == 11


@pytest.mark.parametrize('body', [
    'code: 1234567',  # Do not truncate a longer number.
    'code: 123456 code: 654321',  # Ambiguous message.
    'unrelated 123456',
])
def test_invalid_messages_timeout_without_exposing_body(monkeypatch, body):
    reader = AndroidSmsOtp(timeout=1, marker='test', sender='')
    monkeypatch.setattr(reader, '_query', lambda after=None:
                        [(1, '')] if after is None else [(2, body)])
    ticks = iter([0, 0, 2])
    monkeypatch.setattr('support.android_sms.time.monotonic', lambda: next(ticks))
    monkeypatch.setattr('support.android_sms.time.sleep', lambda _: None)
    reader.arm()
    with pytest.raises(TimeoutError) as error:
        reader.wait_for_code(length=6)
    assert body not in str(error.value)
    assert reader.watermark == 1


def test_unarmed_reader_cannot_read_sms():
    with pytest.raises(RuntimeError, match='arm'):
        AndroidSmsOtp().wait_for_code()


def test_uninspected_completion_branch_is_rejected():
    with pytest.raises(ValueError, match='BOG'):
        Scenario(Bank.TBC, EndPoint.COMPLETED)
