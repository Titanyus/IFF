# Abnahmetests – gleicher Vergleich für beide Stacks

## Testdaten

Vier technische Accounts: Leitung, Verwaltung, Therapie 1, Therapie 2. Drei fiktive Kinder mit drei Förderfällen, mindestens ein wartender, aktiver und abgeschlossener Förderfall. Therapeuten unterschiedliche Fälle zugewiesen.

## Funktional

1. Login/Logout mit gültigem/ungültigem Passwort.
2. Warteliste zeigt ausschließlich `waiting`-Fälle, keine zweite Datenspeicherung.
3. Verwaltung legt Kind + verknüpfte Bezugsperson + wartenden Förderfall an.
4. Leitung/Verwaltung aktiviert wartenden Förderfall **nur mit Startdatum**.
5. Abschluss ist **nur bei aktivem Fall** und gültigem Enddatum möglich.
6. Jeder Statuswechsel erzeugt Audit-Eintrag mit Benutzer/Datum.
7. Leitung kann einen Fall in Papierkorb verschieben und daraus wiederherstellen.
8. Therapie 1 sieht Fälle von Therapie 2 nicht, auch nicht über direkte URL/API.
9. Therapie kann keine Statuswechsel-/Papierkorb-Endpunkte ausführen.
10. Daten bleiben nach `docker compose down` und anschließendem `up -d` erhalten.

## Oberfläche

Desktop: Navigation, Tabellen/Filter, Detailansicht. Tablet: lesbar und bedienbar. Smartphone: kompakte Karten statt horizontalem Tabellenzwang. Funktionalität auf dem Mobilgerät kann geringer sein; Backend-Rechte bleiben unverändert.

## Nichtfunktional

- Keine externe Datentransfers durch Anwendungsfrontend; keine CDNs/Google-Fonts.
- Kein direkter PostgreSQL-Port auf Host, Webserver nur localhost.
- Tests müssen nach Anleitung im Container ausführbar sein.
- Kleine, klar nachvollziehbare Abhängigkeiten und nachvollziehbare Modulgrenzen.
- Nicht als produktionsreife Anwendung ausgeben; fehlende Maßnahmen dokumentieren.

## Vergleichsnotizen nach Test

Für beide Varianten bewerten: Verständlichkeit des Codes, benötigte Frameworks/Toolchain, Migrationsqualität, Rechte-Tests, Responsive UX, Geschwindigkeit neuer Änderungen mit Codex und Update-/Deploy-Komplexität. Kein automatischer Gewinner vor praktischen Tests.
