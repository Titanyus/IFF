# Vergleich Rails/Hotwire und Django/Vue – 03.11.2026

## Vorläufige Empfehlung

Für die bisher beschriebene Frühförderverwaltung ist Rails/Hotwire der einfachere Ausgangspunkt für eine Entwicklung mit Codex. Grund ist der kleinere Koordinationsaufwand zwischen den Schichten: Modelle, Policies, Services, Controller und HTML-Views folgen einem gemeinsamen Framework und überwiegend einer Sprache. Hotwire deckt viele interaktive Verwaltungsabläufe ab, ohne einen eigenen TypeScript-Client mit JSON-Vertrag aufzubauen. Dies ist eine Bewertung des konkreten Aufgabenprofils, keine allgemeine Rangliste der Sprachen oder der Codegenerierungsfähigkeiten von Codex.

Django/Vue ist ebenfalls geeignet. Es wird attraktiver, wenn Python-Kompetenz im Team, konkrete Python-Fachanwendungen oder eine umfangreiche interaktive Oberfläche wichtig werden. Das Django-Backend kann sehr übersichtlich sein; in dieser Variante kommt jedoch die eigenständige Vue-Anwendung mit zusätzlicher Toolchain und API-Vertrag hinzu. Ein Django-System mit serverseitigen Templates wäre eine weitere mögliche Architektur, wird durch diesen Vergleich aber nicht getestet.

## Änderungsaufwand mit Codex

| Aspekt | Rails/Hotwire | Django/Vue |
|---|---|---|
| Typische neue Verwaltungsfunktion | Service/Policy, Controller und ERB-View im selben Framework | Service/Policy, JSON-Endpunkt, gegebenenfalls Serialisierung, TypeScript und Vue-View |
| Vorgaben und Muster | Viele feste Rails-Konventionen helfen bei kleinen zusammenhängenden Änderungen | Django ist ebenfalls klar strukturiert; zusätzlich müssen die Frontend-Muster konsistent bleiben |
| Qualitätssicherung | Backend-/Integrationstests; UI und JS bei Bedarf separat | Backendtests plus TypeScript/Frontend-Build; für die Verbindung später Browsertests |
| Abhängigkeiten und Updates | Ruby/Gems und lokale Hotwire-Assets; kein npm-Build in diesem PoC | Python-Pakete plus npm-Abhängigkeiten und Vue-/Vite-Build |
| Umfangreiche lokale UI-Interaktion | Hotwire kann viel abdecken; zusätzliche JS-Logik steigt mit der UI-Komplexität | Vue hat Vorteile bei umfangreichem Zustand und vielen unmittelbar miteinander reagierenden Komponenten |

Codex kann beide Stacks bearbeiten. Entscheidend sind wiederkehrende Konventionen, klare Fachvorgaben und Tests für Rechte, Status und Audit. Python-Syntax allein reduziert den Gesamtaufwand einer Python-plus-TypeScript-Anwendung nicht automatisch. Der vorhandene Django-PoC nutzt keine zusätzliche REST-Framework-Bibliothek, sondern kleine Django-Views; das hält ihn bewusst klein.

## Beobachtungen aus der Einrichtung

Beide Stacks ließen sich bauen und mit PostgreSQL betreiben. Rails: sechs Tests mit 31 Assertions erfolgreich. Django: fünf Tests erfolgreich; Vue: TypeScript-Prüfung und Produktionsbuild erfolgreich. HTTP-Prüfungen bestätigen die vier Rollen, fremde Fall-IDs, CSRF, Login und Logout für beide Varianten.

Die Startvorlagen enthielten korrigierbare Lücken: falsche Rails-Demogruppen, fehlende Rails-Testkonfiguration, fehlendes Nginx-Webverzeichnis bei Django/Vue sowie Django-ID-Metadaten ohne passende Folgemigration. Diese Befunde bewerten die Vorlage und sind kein Beleg für eine grundsätzliche Schwäche des jeweiligen Frameworks.

Die erste Ruby-Abhängigkeitsauflösung dauerte mehrere Minuten: `index.rubygems.org` war nicht freigegeben, Bundler verwendete den regulären vollständigen RubyGems-Index als Fallback. Diese Zeit ist kein fairer Vergleich von Rails gegen Python und sagt nichts über den laufenden Betrieb. Lockdateien und Docker-Layer-Caches reduzieren Wiederholungsaufwand; Änderungen an normalen Anwendungsdateien installierten beim abschließenden Wiederholungsbuild keine Abhängigkeiten neu.

## Lokale Messung und ihre Grenzen

Einzelne Momentaufnahme auf derselben Cloud-Maschine; drei fiktive Fälle, Verwaltungsanmeldung, fünf Aufwärmabrufe, danach je 50 abwechselnde sequenzielle Listenabrufe über Nginx. Gemessen wurde die vollständige HTTP-Antwort aus Sicht eines Python-Clients; kein Browser, keine parallelen Nutzer und keine vollständige Nutzerinteraktion.

| Messgröße | Rails/Hotwire | Django/Vue |
|---|---:|---:|
| Median Listenabruf | 13,60 ms | 23,75 ms |
| p95 Listenabruf, einfacher Ordnungsstatistik-Schätzer | 21,09 ms | 29,54 ms |
| Web-Container-RAM im weitgehend ruhenden Zustand | ca. 105 MiB | ca. 92 MiB |
| Web-Image, unkomprimiert laut Docker | ca. 573 MB | ca. 217 MB |

Die Rails-Antwort enthält serverseitig erzeugtes HTML, die Django-Antwort JSON. Rails läuft mit Puma im Entwicklungsmodus; Django mit Gunicorn, zwei Workern und `DEBUG=0`. Deshalb sind die Zahlen **kein fairer Framework-Benchmark und keine Kapazitätsprognose**. Sie zeigen lediglich, dass beide Demos auf dieser Maschine schnell antworten. Die gemessene Differenz beweist keinen Vorteil von Ruby gegenüber Python. Die RAM-Werte schwanken mit Last, Arbeitern und Caches; der geringe Unterschied ist für die Stackentscheidung wenig aussagekräftig. Imagegröße ist kein RAM-Bedarf. Im Rails-Image bleiben Compiler/Buildwerkzeuge enthalten; ein späterer mehrstufiger Build könnte es verkleinern.

Nginx benötigt in beiden Varianten zusätzlich etwa 6 MiB RAM; jede Variante betreibt außerdem ihren eigenen PostgreSQL-Container. Für Vue läuft im normalen Betrieb kein Node-Server: Node wird nur zum Build benötigt, Nginx liefert danach statische Dateien aus. Der Python-Web-Container ist daher nicht die gesamte Variante; das gebaute Nginx/Vue-Image umfasst zusätzlich ca. 62 MB. Rails benötigt ebenfalls Nginx.

## Unterschiede im Betrieb

Beide haben hier dieselbe grobe Struktur: Nginx, ein Anwendungscontainer, PostgreSQL, getrennte Datenvolumes und Migrationen. Backup, Restore, HTTPS und Updates bleiben für beide erforderlich. Für eine Einrichtung mit etwa 20 Beschäftigten gibt es aus diesem PoC keinen Hinweis, dass die grundsätzliche Leistungsfähigkeit einer der beiden Architekturen die Entscheidung bestimmen sollte. Eine konkrete Kapazität wurde nicht getestet.

Bei Rails erzeugt der Server HTML; Turbo kann Teile davon aktualisieren. Bei Django/Vue lädt der Browser zunächst die gebauten JavaScript-Dateien und erzeugt Ansichten aus API-Daten. Das kann bei umfangreicher UI-Interaktion hilfreich sein, bringt aber zusätzliche Clientlogik und Frontend-/API-Abstimmung mit. Eine SPA beseitigt weder Backendabfragen noch Netzwerklatenz und ist nicht automatisch schneller.

Bei wachsenden Fallzahlen sind Datenbankabfragen, Indizes, Pagination und Datenmengen voraussichtlich wichtiger als die Sprache. Konkret lädt die Django-Liste Bezugspersonen fallweise nach; dies sollte vor größeren Datenmengen durch gezieltes Prefetching geprüft werden. Auch wiederholte Rollenabfragen verdienen Messung. Im PoC fehlt eine repräsentative Lastprüfung bei beiden Stacks.

## Entscheidungsvorschlag

Rails/Hotwire als vorläufigen Favoriten behandeln, ohne den anderen Stack bereits zu entfernen. Für eine belastbare Entscheidung dieselbe kleine fachliche Erweiterung nacheinander in beiden Varianten umsetzen lassen, beispielsweise einen weiteren Förderfall zu einem vorhandenen Kind. Zuerst fachliche Freigabe und identische Akzeptanzkriterien, dann Aufwand für geänderte Dateien, Korrekturrunden, Tests, Verständlichkeit und Bedienung vergleichen. Diese Erweiterung wurde nicht vorweggenommen.

Wenn Performance später entscheidend wird, beide mit vergleichbarer Produktionskonfiguration, repräsentativem synthetischem Datenbestand und gleicher Anzahl gleichzeitiger Nutzer messen. Dabei vollständige Nutzeraktionen, p95-Latenz, Fehlerquote, Datenbankabfragen, CPU und RAM erfassen. Erst damit lässt sich Hardware dimensionieren oder eine Lastgrenze begründen.
