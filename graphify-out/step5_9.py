import sys, json
from graphify.build import build_from_json
from graphify.cluster import score_all
from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.report import generate
from pathlib import Path

def step5():
    extraction = json.loads(Path('graphify-out/.graphify_extract.json').read_text(encoding="utf-8"))
    detection  = json.loads(Path('graphify-out/.graphify_detect.json').read_text(encoding="utf-8-sig"))
    analysis   = json.loads(Path('graphify-out/.graphify_analysis.json').read_text(encoding="utf-8"))

    G = build_from_json(extraction, root='.', directed=False)
    communities = {int(k): v for k, v in analysis['communities'].items()}
    cohesion = {int(k): v for k, v in analysis['cohesion'].items()}
    tokens = {'input': extraction.get('input_tokens', 0), 'output': extraction.get('output_tokens', 0)}

    labels = {
        0: "Records Admin and Models",
        1: "Events Admin and Models",
        2: "Events Soft Delete Admin",
        3: "Events Views and URLs",
        4: "Accounts and User Models",
        5: "Django App Configurations",
        6: "Admin Index Templates",
        7: "Django Manage Script",
        8: "Accounts DB Migrations",
        9: "Login Authentication Templates",
        10: "Event Frontend Templates",
        11: "Record Frontend Templates",
        12: "ASGI Deployment Config",
        13: "Django Project Settings",
        14: "Root URL Routing",
        15: "WSGI Deployment Config",
        16: "Events DB Migrations",
        17: "Records DB Migrations",
        18: "Accounts Initialization",
        19: "Accounts Migrations Init",
        20: "Accounts Unit Tests",
        21: "Accounts View Logic",
        22: "Event System Initialization",
        23: "Events Migrations Init",
        24: "Events Unit Tests",
        25: "Records Auto Fill JS",
        26: "Records Migrations Init",
        27: "Records Unit Tests"
    }

    questions = suggest_questions(G, communities, labels)
    report = generate(G, communities, cohesion, labels, analysis['gods'], analysis['surprises'], detection, tokens, '.', suggested_questions=questions)
    Path('graphify-out/GRAPH_REPORT.md').write_text(report, encoding="utf-8")
    Path('graphify-out/.graphify_labels.json').write_text(json.dumps({str(k): v for k, v in labels.items()}, ensure_ascii=False), encoding="utf-8")
    print('Report updated with community labels')

def step9():
    from datetime import datetime, timezone
    from graphify.detect import save_manifest

    detect = json.loads(Path('graphify-out/.graphify_detect.json').read_text(encoding="utf-8-sig"))
    save_manifest(detect.get('all_files') or detect['files'], root='.')

    extract = json.loads(Path('graphify-out/.graphify_extract.json').read_text(encoding="utf-8"))
    input_tok = extract.get('input_tokens', 0)
    output_tok = extract.get('output_tokens', 0)

    cost_path = Path('graphify-out/cost.json')
    if cost_path.exists():
        cost = json.loads(cost_path.read_text(encoding="utf-8"))
    else:
        cost = {'runs': [], 'total_input_tokens': 0, 'total_output_tokens': 0}

    cost['runs'].append({
        'date': datetime.now(timezone.utc).isoformat(),
        'input_tokens': input_tok,
        'output_tokens': output_tok,
        'files': detect.get('total_files', 0),
    })
    cost['total_input_tokens'] += input_tok
    cost['total_output_tokens'] += output_tok
    cost_path.write_text(json.dumps(cost, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f'This run: {input_tok:,} input tokens, {output_tok:,} output tokens')
    print(f'All time: {cost["total_input_tokens"]:,} input, {cost["total_output_tokens"]:,} output ({len(cost["runs"])} runs)')

if __name__ == '__main__':
    step5()
    step9()
