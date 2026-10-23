"""Quick pre-demo check: python verify_setup.py"""
import sys

from harness.health import run_health_check


def main() -> int:
    report = run_health_check(test_api=True)
    for line in report.messages:
        print(line)
    if report.ok:
        print("\nAll checks passed. Run: streamlit run app.py")
        return 0
    print("\nFix the FAIL items above before your demo.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
