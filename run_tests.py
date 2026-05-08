#!/usr/bin/env python3
"""Run all 20 test scenarios using curl subprocess."""
import json, subprocess, time, os

API = "http://localhost:8001/api/v1/analyze"
TEST_FILE = "/mnt/e/workspace/UserRegister/arch-assistant/data/test_scenarios.json"
PROGRESS_FILE = "/mnt/e/workspace/UserRegister/arch-assistant/test_progress.json"
RESULT_FILE = "/mnt/e/workspace/UserRegister/arch-assistant/test_results.json"

with open(TEST_FILE) as f:
    scenarios = json.load(f)

results = []
passed = 0
failed = 0

def save():
    with open(PROGRESS_FILE, "w") as f:
        json.dump({"current": len(results), "total": len(scenarios),
                   "passed": passed, "failed": failed, "results": results}, f, ensure_ascii=False)

# Clear old progress
save()

for s in scenarios:
    sid = s["id"]
    desc = s["description"]
    exp = s.get("primary_recommendation", "")
    
    t0 = time.perf_counter()
    
    payload = json.dumps({"prompt": desc, "session_id": f"batch_{sid}"})
    proc = subprocess.run([
        "curl", "-s", "--max-time", "180", "-X", "POST", API,
        "-H", "Content-Type: application/json",
        "-d", payload
    ], capture_output=True, text=True, timeout=200)
    
    elapsed = round((time.perf_counter() - t0) * 1000)
    
    if proc.returncode != 0:
        results.append({"id": sid, "desc": desc[:60], "expected": exp,
                       "top": "ERROR", "hit": False, "elapsed": elapsed, "error": proc.stderr[:100]})
        failed += 1
        save()
        continue
    
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        results.append({"id": sid, "desc": desc[:60], "expected": exp,
                       "top": "PARSE_ERR", "hit": False, "elapsed": elapsed})
        failed += 1
        save()
        continue
    
    candidates = data.get("candidates") or []
    top_name = candidates[0]["name"] if candidates else "N/A"
    names = [c["name"] for c in candidates[:3]]
    hit = any(exp in n for n in names)
    
    # 宽松匹配：检查别名匹配
    if not hit:
        alias_map = {
            "CQRS": ["CQRS"],
            "SOA": ["SOA"],
            "MVC": ["MVC", "Model-View-Controller"],
            "P2P": ["P2P", "对等", "Peer"],
            "Serverless": ["Serverless", "无服务器"],
            "Space-Based": ["Space-Based", "空间架构", "SBA"],
        }
        for key, aliases in alias_map.items():
            if key in exp:
                hit = any(any(a.lower() in n.lower() for a in aliases) for n in names)
                break
    
    if hit:
        passed += 1
    else:
        failed += 1
    
    results.append({"id": sid, "desc": desc[:60], "expected": exp,
                   "top": top_name, "candidates": names, "hit": hit, "elapsed": elapsed})
    save()

# Final save
summary = {"passed": passed, "failed": failed, "total": len(scenarios),
           "accuracy": f"{passed}/{len(scenarios)} ({100*passed/len(scenarios):.1f}%)"}
with open(RESULT_FILE, "w") as f:
    json.dump({"summary": summary, "results": results}, f, ensure_ascii=False, indent=2)

print(f"DONE: {summary['accuracy']}")
