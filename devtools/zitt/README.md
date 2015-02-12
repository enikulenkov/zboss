ZBOSS integration testing tool (zitt)
=====================================

Objectives:
- Run provided list of tests
- Provide good reporting about success/failures
- Allow executing the same tests using different platforms (emulator or real
  hardware attached via JTAG, USB or whatever else)
- Provide easy configuration for tests run
- Collecting diagnostic info (mainly trace) for futher issue debugging
- Easy integration with CI tools
- Running on full-fledged Linux using python

Corresponding changes are necessary in tests:
- Every test harness device should report to zitt about start/end of the test.
  Also it reports about any error happened during test execution.
  Reporting is made by means specific to the platform (writing to stdout,
  sending over UART, etc.)
