# AGENTS.md – Verbindliche Anweisungen für Codex

## Ziel und Grenzen

Wir bauen eine kleine, erweiterbare Verwaltung für Kinder und Förderfälle einer eigenständigen Frühförderung; **keine universelle ERP-Plattform**. Die beiden Unterverzeichnisse sind **vergleichbare PoCs**, keine zwei gleichzeitig weiterzuentwickelnden Produktivsysteme. Arbeite nach Entscheidung nur im gewählten Stack.

## Unverhandelbare Regeln

1. **Eine Information, eine Quelle:** Keine redundanten Stammdateneingaben. Kind, Sorgeberechtigte und Förderfall bleiben getrennte, relationale Objekte.
2. **Zentrale Rechteprüfung:** Jede lesende und schreibende Anfrage filtert serverseitig nach dem angemeldeten Benutzer. UI-Ausblenden ersetzt niemals Berechtigungsprüfung. Keine selbst erfundenen Zweitmechanismen.
3. **Fachstatus und Löschstatus trennen:** `waiting`, `active`, `closed` sind Lebenszykluszustände; `deleted_at` bedeutet Papierkorb. Kein Hard Delete im PoC.
4. **Modularer Monolith:** Kein Microservice-, Plugin- oder Event-Bus-System. Fachlogik in klaren Services/Policies, dünne Controller/Views.
5. **Klein halten:** Keine neue Bibliothek ohne nachgewiesenen Nutzen. Keine externen CDN-, Cloud-, Analyse-, Telemetrie- oder Font-Dienste.
6. **Keine echten Daten:** Nur fiktive Namen, Accounts und Dokumente. Keine personenbezogenen Patientendaten in Prompts, Tests, Logs oder Git.
7. **Tests sind Teil der Funktion:** Berechtigungen, Statuswechsel und Audit müssen durch Tests abgedeckt werden. Negative Tests (unbefugter Zugriff) verpflichtend.
8. **Migrationen statt Zurücksetzen:** Änderungen am Schema versioniert; keine destruktiven Datenbank-Reset- oder Löschbefehle gegen bestehende Daten.
9. **Keine stillen Grundsatzentscheidungen:** Bei Änderungen an Datenmodell, Sicherheitsmodell, Modulgrenzen oder externen Abhängigkeiten zuerst Vorschlag + Auswirkungen liefern und Freigabe abwarten.
10. **Sicherheit nicht versprechen:** HTTP auf Loopback und Demo-Passwörter sind ausschließlich PoC. Nichts als DSGVO-konform oder produktionsreif deklarieren.

## Arbeitsablauf

1. Relevante Dateien und dieses Dokument lesen.
2. Eine knappe Änderungsskizze mit Auswirkungen auf Berechtigungen, Daten, API und Tests liefern.
3. Nur die explizit gewünschte Funktion implementieren.
4. Migrationen, Tests und UI bei Bedarf gemeinsam anpassen.
5. Am Ende: geänderte Dateien, Tests/Ergebnisse, Restrisiken und erforderliche manuelle Schritte nennen.

## Qualitätsregeln

- Jeder Statuswechsel ist atomar und auditierbar, einschließlich ausführender Person und Zeitpunkt.
- `waiting → active` erfordert einen Förderbeginn; `active → closed` erfordert ein Abschlussdatum.
- Neue Förderfälle können später für bereits bestehende Kinder eröffnet werden.
- Datenschutzrelevante Zugriffe folgen *deny by default*, nicht „alle, außer ...“.
- Alle UI-Elemente responsiv: Smartphone, Tablet, Desktop. Mobile Funktionalität darf **reduziert** sein, nicht aber die Rechteprüfung.
- Keine direkte Cross-Modul-Manipulation. Für neue Fachfunktionen vorhandene Service-APIs nutzen.
- Zugriffsrechte an Datensätzen nicht mit UI-Komponenten oder CSS koppeln.

## Nicht vorziehen

Ansible, Dockhand, VPN, Backup-Automatisierung, Word-Import, Abrechnung, Statistiken, Löschfristen, Mehrmandantenfähigkeit, Drittanbieterintegration, Offline-PWA sind *später* zu entscheiden. Nicht „vorsorglich“ installieren oder implementieren.
