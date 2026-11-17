# API RP 754 PSE Screening — Android

This project builds an installable Android debug APK for a guided, one-question-at-a-time preliminary Tier 1 / Tier 2 screening workflow.

## Build and download the APK

1. Open the repository's **Actions** tab: https://github.com/Master197/test1/actions
2. Select **Build Android APK** and open the latest run.
3. Wait for the green successful status.
4. Under **Artifacts**, download **API754-PSE-Android-debug**.
5. Extract the ZIP; it contains `app-debug.apk`.
6. Transfer the APK to the Android phone and open it to install. Android may ask you to allow installation from that source.

The workflow also runs automatically when files under `api754-android/` change.

## App features

- One question per screen, with progress and Back / Next navigation.
- Answers remain available when moving backwards.
- Preliminary Tier 1 / Tier 2 / hold / not-Tier-1-or-2 screening.
- Generates a Word `.docx` report containing the result, rationale, unresolved items, event details, and entered answers.
- Uses Android's share sheet to save or share the report.

## Safety and technical limitations

This is a prototype decision-support tool, not an API-certified application. Chemical threshold tables and mixture calculations are not embedded. Fire / explosion cost thresholds must be entered from the controlled current standard and company procedure. The screening logic is simplified and must be validated line-by-line against the licensed current API RP 754 edition and approved site procedure before operational use. Unknown information must be investigated, not treated as No. A competent process-safety professional must review and approve any classification.

The report intentionally labels results as preliminary. A successful APK build does not establish technical or regulatory compliance.
