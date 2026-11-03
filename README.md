# Frühförderverwaltung – Codex Proof of Concept

**Zweck:** Zwei kleine, fachlich möglichst identische Webanwendungen vergleichen. Beide verwenden PostgreSQL und Docker Compose. Alle Beispieldaten sind **frei erfunden**. Kein Produktivsystem, keine echten Patientendaten!

## Schnellstart

Voraussetzung: Docker Engine mit Compose V2 und Internetzugang beim ersten Image-Build.

**Variante A – Rails + Hotwire**

```bash
cd rails-hotwire
cp .env.example .env
docker compose up --build -d
docker compose logs -f web
```

Öffnen: **http://localhost:8081**

**Variante B – Django + Vue 3**

```bash
cd django-vue
cp .env.example .env
docker compose up --build -d
docker compose logs -f web
```

Öffnen: **http://localhost:8082**

Die Varianten verwenden jeweils einen **separaten Datenbank-Container** und getrennte Volumes. Sie können parallel laufen. Daten werden nicht zwischen den Varianten geteilt.

**Demo-Anmeldung** (in beiden Varianten gleich, ausschließlich Testzwecke):

| Login | Passwort | Rolle | Erwartetes Verhalten |
|---|---|---|---|
| `leitung@example.test` | `DemoPass-2026!` | Leitung | Sieht alle Fälle; kann Papierkorb benutzen |
| `verwaltung@example.test` | `DemoPass-2026!` | Verwaltung | Sieht und verwaltet alle aktiven Fälle |
| `therapie1@example.test` | `DemoPass-2026!` | Therapie | Sieht nur zugeordnete Fälle |
| `therapie2@example.test` | `DemoPass-2026!` | Therapie | Sieht andere zugeordnete Fälle |

Für das PoC wird **nur HTTP über 127.0.0.1** veröffentlicht. Zugriff über das LAN ist bewusst nicht aktiviert. Die endgültige HTTPS-/Nginx-/VPN-Konfiguration, Ansible und Borg gehören **nicht** zu diesem PoC. Niemals echte Daten oder produktive Zugänge verwenden.

## Was demonstriert wird

- Anmeldung mit Sitzungscookies, Rollen-Gruppen und serverseitiger Zugriffskontrolle
- Ein Kind hat einen eigenen Stammdatensatz, getrennt von seinen Förderfällen
- Sorgeberechtigte sind separate, verknüpfbare Stammdatensätze
- Warteliste = gefilterte Ansicht von Förderfällen mit Status `waiting`
- Statusfolge `waiting → active → closed` inklusive datierter Übergänge und Audit-Einträgen
- Neue Förderfälle sind konzeptionell getrennt vom Kind; spätere erneute Förderung erfordert keinen neuen Kind-Datensatz
- Soft Delete ist **getrennt** vom fachlichen Status und in beiden Demos nur für Leitung vorgesehen
- Responsive Oberfläche als technischer Vergleich, mit reduzierter Komplexität auf dem Smartphone

## Was bewusst fehlt

**Nicht produktionsreif:** kein HTTPS, kein VPN, kein Backup/Restore, keine gehärtete Authentifizierung mit MFA, keine Oberfläche zur Verwaltung von Benutzerkonten und Gruppen (im PoC über Testdaten vorbereitet), keine fein granulierte Feldberechtigung, kein Dokumentimport, keine Einwilligungs-/Aufbewahrungsregeln, keine Audit-Manipulationssicherung, keine fachlich validierten Workflows, keine Datenschutz-Folgenabschätzung und keine getesteten Restore-Prozeduren. Keine Nutzung mit realen Kinder-/Gesundheitsdaten.

## Testen

```bash
cd rails-hotwire
docker compose exec -e RAILS_ENV=test web bundle exec rails db:create db:migrate
docker compose exec -e RAILS_ENV=test web bundle exec rails test

cd ../django-vue
docker compose exec web python manage.py test records
```

Manuell: Als `therapie1` anmelden, zugeordnete Fälle sehen; auf Fälle von `therapie2` darf kein Zugriff bestehen. Danach als Verwaltung anmelden, Warteliste ansehen, einen Fall aktivieren (Startdatum verpflichtend) und abschließen. Als Leitung einen Fall in den Papierkorb verschieben/wiederherstellen. Die Oberfläche ist **keine** Berechtigungsgrenze: Backend-Tests prüfen diese separat.

## Stoppen und Neustarten

```bash
docker compose down       # Container stoppen, Datenvolumen bleibt
docker compose up -d      # Daten sollen erhalten bleiben
```

`docker compose down -v` **löscht die Demo-Datenvolumes**. Bei echten Daten niemals ohne geprüftes Backup verwenden.

## Abhängigkeits- und Versionspolitik

Die Einrichtung vom 03.11.2026 ergänzt `Gemfile.lock`, `requirements.lock` mit Hashes sowie `package-lock.json`. Die Docker-Builds verwenden `BUNDLE_FROZEN=true`, `pip --require-hashes` und `npm ci`; Basisimages sind mit Digests fixiert. Sicherheitsupdates werden kontrolliert übernommen. Für Builds hinter einem HTTPS-Proxy ist ein optionales CA-Bundle vorgesehen; Details, Prüfresultate und offene Abnahme in [SETUP_REPORT.md](docs/SETUP_REPORT.md).

## Projektunterlagen

- [DOCKHAND.md](docs/DOCKHAND.md) – Git-Stacks für Rails auf Port 2501 und Django/Vue auf Port 2502

- [SETUP_REPORT.md](docs/SETUP_REPORT.md) – Einrichtung und Prüfergebnisse
- [STACK_COMPARISON.md](docs/STACK_COMPARISON.md) – Codex-Entwicklung, Betrieb und Performance

- [VISION.md](docs/VISION.md) – Ziel und Produktprinzipien
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) – Grenzen und Bausteine
- [DATA_MODEL.md](docs/DATA_MODEL.md) – Fachliches Datenmodell
- [SECURITY.md](docs/SECURITY.md) – Sicherheitsziele und PoC-Grenzen
- [ACCEPTANCE.md](docs/ACCEPTANCE.md) – Vergleichbare Akzeptanztests
- [DECISIONS.md](docs/DECISIONS.md) – Architekturentscheidungen
- [CODEX_START.md](docs/CODEX_START.md) – Startprompt und Entwicklungsablauf
- [AGENTS.md](AGENTS.md) – Verbindliche Arbeitsregeln für Codex

Technologien: Ruby on Rails/Hotwire bzw. Django/Vue/PostgreSQL, als isolierte Tests. Ansible und Produktiv-Infrastruktur folgen erst nach der Technologieentscheidung.
