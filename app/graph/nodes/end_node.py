"""
end_node.py
-----------
Terminal node that handles project completion or failure.
"""


def end_node(state):
    """
    End node - handles both successful completion and failures.
    """
    tests_passed = state.get("tests_passed", False)
    repair_attempts = state.get("repair_attempts", 0)
    project_dir = state.get("project_dir", "unknown")
    
    print("\n" + "=" * 60)
    
    if tests_passed:
        print("🎉 PROJECT GENERATION SUCCESSFUL!")
        print("=" * 60)
        print(f"\n📁 Your project is ready at: {project_dir}")
        print("\nTo run manually:")
        print(f"   1. cd {project_dir}/backend && python app.py")
        print(f"   2. cd {project_dir}/frontend && npm install && npm run dev")
        print(f"   3. Open http://localhost:5173 in your browser")
    else:
        print("⚠️ PROJECT GENERATION COMPLETED WITH ISSUES")
        print("=" * 60)
        print(f"\n📁 Partial project at: {project_dir}")
        print(f"   Repair attempts made: {repair_attempts}/3")
        
        error = state.get("error_message")
        if error:
            print(f"\n❌ Last error:\n   {error[:200]}...")
        
        print("\n💡 You may need to manually fix the remaining issues.")
    
    print("\n" + "=" * 60)
    
    return state
