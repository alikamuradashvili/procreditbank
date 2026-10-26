# Consumer loan automation

One test class, three named test methods, and one reusable orchestration method:

```python
flow.fill_application(loan_data, mobile, Scenario(Bank.BOG, EndPoint.COMPLETED),
                      same_address=True, is_pep=False)
```

`Scenario` controls bank, endpoint, marketing, and individual `Consents` fields.
`LoanData` controls amount, term, purpose, and currency. Page objects contain selectors,
explicit waits, actions, and assertions. No `sleep` calls are used for browser steps.
The SMS poll interval is one second; only matching fresh messages are used.

## Cases

| Pytest case ID | Endpoint |
| --- | --- |
| test_01_loan_application_otp_bog_complete | Initial 6-digit OTP → BOG selection → fresh 4-digit BOG OTP → personal details → configured consents → success assertions |
| test_02_loan_application_otp_tbc_selection | Initial OTP → select TBC and verify selection; no TBC confirmation request |
| test_03_loan_application_otp_identomat_selection | Initial OTP → select Identomat and verify selection; stop before starting video identification |

The observed verification options were `bog`, `tbc`, and `Identomat`. Identomat is
not substituted for ProCredit. TBC and ProCredit completion flows are not verified.
Different legal/actual addresses and PEP details are not implemented; unsupported
branches fail before opening a browser. The marketing custom toggle assumes a fresh
identification form and retains its state within the page object.

Completion stays on `/loan-application/about-services`. Assertions require all three
observed success texts and disappearance of the consent form and submit button.
This indicates application completion, not credit approval.

## Run in the project directory

Keep the existing `.env`; set `same_address=True` and `is_pep=False` in the test only
if those declarations apply to the applicant. See `.env.example`. Connect and authorize
the Android phone for ADB. OTP values and SMS bodies are not logged or saved.

```powershell
# Full BOG case, including configured consents and application submission:
.\.venv\Scripts\python.exe -m pytest tests/test_consumer_loan_application.py -k test_01_loan_application_otp_bog_complete --live --complete-application -s
# TBC selection only:
.\.venv\Scripts\python.exe -m pytest tests/test_consumer_loan_application.py -k test_02_loan_application_otp_tbc_selection --live -s
# Identomat selection:
.\.venv\Scripts\python.exe -m pytest tests/test_consumer_loan_application.py -k test_03_loan_application_otp_identomat_selection --live -s
# Local tests, no bank or phone access:
.\.venv\Scripts\python.exe -m pytest tests/test_sms_reader.py -q
```

In IntelliJ use a Python module configuration: module `pytest`, working directory
the project root, interpreter `.venv/Scripts/python.exe`, and the parameters above.
The three provided run configurations select only their named case. Old Form/OTP
configurations use obsolete arguments and should be replaced.

This refactor has not been executed end-to-end against the live bank. Its BOG steps
were previously observed interactively. Run only the intended case to avoid creating
multiple applications. No automatic retries or OTP resends are performed.
