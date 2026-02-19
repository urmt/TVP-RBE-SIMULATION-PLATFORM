# CODER INSTRUCTIONS for AI Agents (VS Code)

This file provides guidance for AI coding agents (Copilot, Cursor, etc.) working in this repository.

## Project Overview
**Repository:** RBE-TVP-SIM  
**Location:** `/home/student/RBE-TVP-SIM`  
**Primary Development Environment:** Warp Terminal with AI Agent Mode

## Important Context Files

### 1. WARP.md (Project-Specific Rules)
- **Purpose:** Contains project-specific coding standards, conventions, and AI agent instructions
- **Location:** `./WARP.md` (root of this repository)
- **Priority:** HIGH - These rules override global Warp rules
- **Usage:** Read this file first to understand project-specific requirements

### 2. Subdirectory WARP.md Files
- **Purpose:** Module or component-specific rules that override parent directory rules
- **Search Pattern:** `**/WARP.md` (recursively in subdirectories)
- **Priority:** HIGHEST - Most specific rules take precedence
- **Rule Precedence:** Subdirectory rules > Root WARP.md > Global rules

### 3. Log Files
- **Search Pattern:** `**/*.log`
- **Purpose:** Contains execution logs, error traces, and runtime information
- **Usage:** Reference when debugging or understanding past behavior

### 4. Global Warp Rules
The user has established the following global coding standards for ALL projects:

#### Best Practices Standards
- **Comments:** Always include descriptive comments sufficient for novice programmers to understand
- **Error Checking:** Implement error checking for any procedure with complexity
- **Code Quality:** Write code that is easily usable by intermediate programmers

#### GitHub Integration
- **Repository Pattern:** Check for existence of `github.com/urmt/[project-name]`
- **Push Timing:** Upon 80% completion of successfully running project, prompt to push to GitHub
- **Commit Message Format:** Include co-author line for Warp contributions:
  ```
  Co-Authored-By: Warp <agent@warp.dev>
  ```

#### External AI LLM Usage
- **Cost Optimization:** When external AI LLMs can be used to save Warp credits, provide:
  - Copyable prompts for external AI LLMs
  - Instructions for integrating the output back into the workflow
- **Trigger:** Inform at the time the opportunity arises

#### Documentation Requirements
- **WARP.md Files:** Always prompt for creation/initialization (use `/init` command in Warp)
- **Subdirectory WARP.md:** Create in subdirectories of large projects for efficiency

## File Discovery Commands

### Find All WARP.md Files
```bash
find /home/student/RBE-TVP-SIM -name "WARP.md" -type f
```

### Find All Log Files
```bash
find /home/student/RBE-TVP-SIM -name "*.log" -type f
```

### Find Documentation Files
```bash
find /home/student/RBE-TVP-SIM -name "*.md" -o -name "*.txt" -type f
```

## Existing Project Files

### Planning Documents
- `SELL plan.txt` - Sales/business planning document
- `Systems Analysis.txt` - Technical systems analysis documentation

## Coding Standards Summary

1. **Comments:** Comprehensive and novice-friendly
2. **Error Handling:** Mandatory for complex procedures
3. **Code Style:** Follow best practices for the language in use
4. **Documentation:** Keep WARP.md files updated with project-specific conventions
5. **Version Control:** Use GitHub at github.com/urmt/ when available

## Context Loading Priority

When starting work on this project:
1. Read `./WARP.md` (if exists) for project-specific rules
2. Check subdirectory WARP.md files for module-specific rules
3. Review relevant log files for debugging context
4. Reference planning documents (`SELL plan.txt`, `Systems Analysis.txt`)
5. Apply global Warp rules (documented above) as baseline

## Notes for AI Agents

- **Rule Precedence:** Most specific (subdirectory) → Project (root) → Global
- **Credit Efficiency:** Suggest external LLM usage when it saves computational resources
- **Collaboration:** Code is co-created with Warp AI; acknowledge in commits
- **Initialization:** If WARP.md doesn't exist, prompt user to create it with `/init`

---

*This file was created to bridge Warp AI Agent Mode context with VS Code AI coding agents.*  
*Last Updated: 2025-12-26*
