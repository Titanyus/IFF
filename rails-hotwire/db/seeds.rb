# Fictional, idempotent demo data. Never use with real records.
users = {}
{ "leitung" => "Leitung", "verwaltung" => "Verwaltung", "therapie1" => "Therapie", "therapie2" => "Therapie" }.each do |slug, label|
  role_slug = slug.start_with?("therapie") ? "therapie" : slug
  group = Group.find_or_create_by!(slug: role_slug) { |g| g.label = label }
  email = "#{slug}@example.test"
  user = User.find_or_create_by!(email: email) { |u| u.password = "DemoPass-2026!" }
  GroupMembership.find_or_create_by!(user: user, group: group)
  users[slug] = user
end

if CareCase.none?
  shared_guardian = Guardian.create!(full_name: "Alex Beispiel")
  [["Emma", "Beispiel", Date.new(2026, 10, 12), "waiting", "therapie1"],
   ["Leon", "Muster", Date.new(2026, 9, 18), "active", "therapie2"],
   ["Mia", "Demo", Date.new(2026, 8, 25), "closed", "therapie1"]].each do |first, last, date, status, therapist|
    child = Child.create!(first_name: first, last_name: last)
    guardian = %w[Emma Mia].include?(first) ? shared_guardian : Guardian.create!(full_name: "Pat Demo")
    ChildGuardian.create!(child: child, guardian: guardian)
    record = CareCase.create!(child: child, requested_on: date, status: status,
                              started_on: (status != "waiting" ? Date.new(2026, 9, 25) : nil),
                              ended_on: (status == "closed" ? Date.new(2026, 10, 30) : nil))
    CaseAssignment.create!(care_case: record, user: users.fetch(therapist))
    AuditEvent.create!(care_case: record, actor: users.fetch("leitung"), action: "seed", to_status: status)
  end
  puts "Fiktive Testdaten angelegt."
else
  puts "Testfälle bereits vorhanden, keine Überschreibung."
end
