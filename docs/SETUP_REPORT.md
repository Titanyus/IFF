# Einrichtung und Prüfbericht – 03.11.2026

## Übernommener Stand

Alle 91 Dateien aus `FF_Codex_PoC_KOMPLETT_NEU.zip` wurden ins Repository übernommen. Alle neun mitgelieferten Markdown-Dateien wurden gelesen. Die Beispielprompts in `CODEX_START.md` sind dokumentierte Vorschläge, keine automatisch auszuführenden Folgeaufträge.

Beide Vergleichsvarianten bleiben getrennt; keine Technologieentscheidung und keine neuen Fachfunktionen. Lokale `.env`-Dateien wurden aus den Beispielen erstellt und bleiben von Git ausgeschlossen. Nur fiktive Demodaten, keine Veröffentlichung.

## Änderungen für die Einrichtung

- Docker-Builds akzeptieren optional ein CA-Bundle als BuildKit-Secret. `compose.cloud.yaml` bindet dieses für die verwaltete Umgebung ein; Zertifikatsprüfung bleibt eingeschaltet.
- Django/Vue-Nginx erhält `root /usr/share/nginx/html` und `index index.html`. Ohne `root` wurde die Startseite mit HTTP 500 ausgeliefert.
- Rails-Seeds ordnen beide Therapiekonten der bestehenden Rolle `therapie` zu. Zuvor wurden Gruppen `therapie1` und `therapie2` angelegt, die die Policy nicht erkennt. Ein Regressionstest prüft Sichtbarkeit, fremde Detailseiten und wiederholte Seeds.
- Django-Folgemigration `0002_align_auto_id_metadata` gleicht die ID-Metadaten an die vorhandenen Modelle an. Typ bleibt `BigAutoField`; keine Datenlöschung und kein fachlicher Modellwechsel.
- `Gemfile.lock`, `requirements.lock` (mit Hashes), `package-lock.json` sowie Basisimage-Digests fixieren die Abhängigkeiten.
- Rails erhält `config/cable.yml` mit lokalen Adaptern (`async` / `test`) und die übliche CSRF-Ausnahme ausschließlich für Integrationstests. Die Demo behält ihren CSRF-Schutz. Die Testanleitung legt die separate Testdatenbank nichtdestruktiv an.

## Start in dieser Cloud-Umgebung

Im jeweiligen Stack-Verzeichnis:

```bash
docker compose -f compose.yaml -f compose.cloud.yaml build
docker compose up -d --no-build
```

`FF_BUILD_CA_BUNDLE` kann auf ein anderes kombiniertes CA-Bundle zeigen; Standard ist `/etc/ssl/certs/ca-certificates.crt`. Docker benötigt hier Zugriff auf den lokalen Daemon außerhalb der Dateisandbox. Auf einem regulären Rechner gilt weiterhin der Schnellstart in der README.

- Rails/Hotwire: `http://127.0.0.1:8081`
- Django/Vue: `http://127.0.0.1:8082`

Diese Adressen beziehen sich auf die Maschine, auf der Docker läuft. Cloud-Loopback ist nicht der lokale Rechner des Benutzers. Es wurde keine öffentliche Freigabe eingerichtet.

Demo: `leitung@example.test`, `verwaltung@example.test`, `therapie1@example.test`, `therapie2@example.test`; Passwort jeweils `DemoPass-2026!`.

## Verifizierte Ergebnisse

- Django: 5 Tests bestanden, Systemcheck ohne Befund; `makemigrations --check --dry-run` meldet keine Änderungen.
- Vue: TypeScript-Prüfung und Vite-Build mit `npm ci` erfolgreich.
- Rails: 6 Tests, 31 Assertions, keine Fehler/Fehlschläge/übersprungenen Tests. Darin enthalten: vorhandene fünf Rechte-/Statustests und Demogruppen-Regression.
- Rails-HTTP: alle vier Accounts, falsches Passwort, CSRF-Ablehnung bei fehlendem Token, erwartete Fallzahlen (3/3/2/1), Detailzugriff, fremde Fall-IDs und Logout geprüft.
- Django-HTTP: alle vier Accounts, falsches Passwort, CSRF-Ablehnung, erwartete Fallzahlen (3/3/2/1), Detailzugriff, fremde Fall-IDs und Logout geprüft.
- Beide Stacks: Fälle, Status und Auditanzahl nach `down` und `up` unverändert; Seeds überschreiben vorhandene Fälle nicht.
- Beide Stack-Builds mit fixierten Abhängigkeiten und die wiederverwendbaren Installations-/Startkommandos erfolgreich ausgeführt.

## Gespeicherter Konfigurationsentwurf

Installationsskript und Startanweisungen für beide Stacks wurden über die Cloud-Environment-Onboarding-Skill als Entwurf gespeichert. Die benutzerdefinierte Netzwerkfreigabe ergänzt ausschließlich `index.rubygems.org`, damit Bundlers normaler Compact Index künftig nutzbar ist; vorhandene Paketmanager-Presets bleiben erhalten. Der aktuelle Build gelang über den regulären RubyGems-Fallback. Die zusätzliche Domain ist in dieser laufenden Instanz noch nicht aktiviert oder validiert. Nichts wurde veröffentlicht; eine Aktivierung der gespeicherten Konfiguration bleibt ein späterer Schritt des Benutzers.

## Grenzen und offene Abnahme

Die mitgelieferten Tests decken nicht alle zehn Akzeptanzfälle vollständig ab: insbesondere fehlt eine vollständige automatisierte Prüfung von Neuanlage samt Bezugsperson, sämtlichen erlaubten/verbotenen Übergängen, Audit-Rollback bei Fehlern und persistierenden Daten nach `down`/`up`. Lokale Neustart-Persistenz wurde bei beiden Stacks geprüft. Responsive CSS ist vorhanden; eine visuelle Browserabnahme auf Smartphone, Tablet und Desktop steht aus. Kein automatischer Gewinner zwischen den Stacks.

Der PoC bleibt auf Loopback-HTTP beschränkt und ist nicht für echte Kinder-/Gesundheitsdaten oder Produktivbetrieb eingerichtet. Die weiteren Grenzen aus `SECURITY.md` gelten unverändert. Die nächste fachliche Funktion wird erst anhand eines konkreten Auftrags geplant.

## Entscheidungshilfe

Die konkrete Einschätzung zu Codex-Entwicklungsaufwand, Betrieb und begrenzter lokaler Performance-Messung steht in [STACK_COMPARISON.md](STACK_COMPARISON.md). Vorläufiger Favorit für den beschriebenen Verwaltungsumfang: Rails/Hotwire. Keine Stackentscheidung wurde umgesetzt.
