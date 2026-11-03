require "test_helper"

class AccessTest < ActionDispatch::IntegrationTest
  setup do
    @therapy = User.create!(email: "therapist-test@example.test", password: "TestPassword123!")
    @other = User.create!(email: "other-test@example.test", password: "TestPassword123!")
    @manager = User.create!(email: "office-test@example.test", password: "TestPassword123!")
    @leader = User.create!(email: "leader-test@example.test", password: "TestPassword123!")
    { @therapy => "therapie", @other => "therapie", @manager => "verwaltung", @leader => "leitung" }.each do |user, slug|
      group = Group.find_or_create_by!(slug: slug) { |g| g.label = slug }
      GroupMembership.create!(user: user, group: group)
    end
    @record = CareCase.create!(child: Child.create!(first_name: "Test", last_name: "Kind"), requested_on: Date.new(2026, 10, 1))
    CaseAssignment.create!(care_case: @record, user: @therapy)
  end

  def login_as(user)
    post session_path, params: { email: user.email, password: "TestPassword123!" }
    follow_redirect!
  end

  test "anonymous users cannot see cases" do
    get care_cases_path
    assert_redirected_to new_session_path
  end

  test "therapist scope hides unrelated cases" do
    login_as(@other)
    get care_cases_path(status: "all")
    assert_response :success
    assert_select "h3", text: "Test Kind", count: 0
    get care_case_path(@record)
    assert_response :not_found
  end

  test "therapist cannot manipulate status" do
    login_as(@therapy)
    patch activate_care_case_path(@record), params: { effective_on: "2026-10-02" }
    assert_response :forbidden
    assert_equal "waiting", @record.reload.status
  end

  test "manager transition is audited and requires valid date" do
    login_as(@manager)
    patch activate_care_case_path(@record), params: { effective_on: "2026-09-01" }
    assert_redirected_to care_case_path(@record)
    assert_equal "waiting", @record.reload.status
    patch activate_care_case_path(@record), params: { effective_on: "2026-10-02" }
    assert_equal "active", @record.reload.status
    assert AuditEvent.exists?(care_case: @record, actor: @manager, action: "status", to_status: "active")
  end

  test "trash is restricted to leadership" do
    login_as(@manager)
    patch trash_care_case_path(@record)
    assert_response :forbidden
    delete session_path
    login_as(@leader)
    patch trash_care_case_path(@record)
    assert @record.reload.deleted?
    patch restore_care_case_path(@record)
    assert_not @record.reload.deleted?
  end
end
