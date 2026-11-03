# Codex-Start und Arbeitsmodus

## Vorschlag für den ersten Prompt an Codex

> Lies zuerst `AGENTS.md`, `docs/VISION.md`, `docs/ARCHITECTURE.md`, `docs/DATA_MODEL.md`, `docs/SECURITY.md` und `docs/ACCEPTANCE.md`. Prüfe danach beide PoC-Implementierungen auf Startbarkeit, Rechteprüfung, atomare Statuswechsel, Audit-Logging und Responsive UI. **Ändere noch nichts.** Erstelle zuerst einen knappen Bericht zu Risiken, fehlenden Tests, konkreten Verbesserungen und etwaigen Unterschieden zur gemeinsamen Spezifikation. Gib die exakten Kommandos für den Docker-Start an. Keine neuen Features, keine zusätzlichen Bibliotheken, keine Umgestaltung der Architektur ohne meine Freigabe.

## Zweiter Prompt: Gezielt testen

> Führe die vorhandenen Tests beider Stacks im Docker-Setup aus. Ergänze nur Tests, die für die zehn Akzeptanzfälle aus `docs/ACCEPTANCE.md` fehlen. Bevor du eine Sicherheitslücke behebst, erkläre kurz Ursache und die kleinste mögliche Änderung. Keine echten personenbezogenen Daten verwenden.

## Dritter Prompt: Featureplanung

> Entwirf, noch ohne Implementierung, die Möglichkeit, zu einem bestehenden Kind einen **weiteren** wartenden Förderfall anzulegen. Prüfe, welche vorhandenen Tabellen/Policies und Views wiederverwendet werden können. Kein Duplizieren des Kindes, keine neue Wartelistentabelle. Liste Migrationen, Tests und UI-Änderungen getrennt auf. Warte danach auf meine Freigabe.

## Regeln für spätere Weiterentwicklung

- Kleine nachvollziehbare Änderungen statt großer Automatik-Refactorings.
- Nach jedem Schritt Tests für Zugriffsrechte.
- Keine künstlichen Frameworks/Plugin-Schnittstellen auf Vorrat.
- Nicht die Wünsche nach Buttons implementieren, bevor das fachliche Ziel bekannt ist.
- Reproduzierbares Docker-Setup, Git-Versionierung, spätere automatisierte Restore-Probe.
