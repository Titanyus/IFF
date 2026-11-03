require "test_helper"

class DemoSeedTest < ActionDispatch::IntegrationTest
  test "seeded therapists can read exactly their assigned cases" do
    Rails.application.load_seed
    first = User.find_by!(email: "therapie1@example.test")
    second = User.find_by!(email: "therapie2@example.test")
    assert first.in_group?("therapie")
    assert second.in_group?("therapie")
    assert_equal 2, CareCaseAccess.scope(first).count
    assert_equal 1, CareCaseAccess.scope(second).count
    assert_empty CareCaseAccess.scope(first).where(id: second.assigned_care_cases.select(:id))

    [first, second].each do |user|
      post session_path, params: { email: user.email, password: "DemoPass-2026!" }
      get care_cases_path(status: "all")
      assert_response :success
      user.assigned_care_cases.each do |record|
        get care_case_path(record)
        assert_response :success
      end
      other_case = CareCase.where.not(id: user.assigned_care_cases.select(:id)).first!
      get care_case_path(other_case)
      assert_response :not_found
      delete session_path
    end

    counts = [User.count, Group.count, GroupMembership.count, Child.count, CareCase.count, AuditEvent.count]
    Rails.application.load_seed
    assert_equal counts, [User.count, Group.count, GroupMembership.count, Child.count, CareCase.count, AuditEvent.count]
  end
end
