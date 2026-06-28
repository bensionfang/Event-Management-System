import sys, json
from pathlib import Path
from graphify.build import build_from_json
from graphify.cluster import cluster, score_all
from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.report import generate
from graphify.export import to_json
from graphify.diagnostics import diagnose_extraction, format_diagnostic_report

def main():
    extraction = json.loads(Path('graphify-out/.graphify_extract.json').read_text(encoding="utf-8"))
    detection  = json.loads(Path('graphify-out/.graphify_detect.json').read_text(encoding="utf-8-sig"))

    G = build_from_json(extraction, root='.', directed=False)
    if G.number_of_nodes() == 0:
        print('ERROR: Graph is empty - extraction produced no nodes.')
        print('Possible causes: all files were skipped, binary-only corpus, or extraction failed.')
        raise SystemExit(1)
    communities = cluster(G)
    cohesion = score_all(G, communities)
    tokens = {'input': extraction.get('input_tokens', 0), 'output': extraction.get('output_tokens', 0)}
    gods = god_nodes(G)
    surprises = surprising_connections(G, communities)
    labels = {cid: 'Community ' + str(cid) for cid in communities}
    questions = suggest_questions(G, communities, labels)

    wrote = to_json(G, communities, 'graphify-out/graph.json')
    if not wrote:
        print('ERROR: refused to shrink graphify-out/graph.json (existing graph has more nodes; #479).')
        print('If this shrink is intentional (you deleted files), re-run a full build with --force.')
        raise SystemExit(1)
    report = generate(G, communities, cohesion, labels, gods, surprises, detection, tokens, '.', suggested_questions=questions)
    Path('graphify-out/GRAPH_REPORT.md').write_text(report, encoding="utf-8")
    analysis = {
        'communities': {str(k): v for k, v in communities.items()},
        'cohesion': {str(k): v for k, v in cohesion.items()},
        'gods': gods,
        'surprises': surprises,
        'questions': questions,
    }
    Path('graphify-out/.graphify_analysis.json').write_text(json.dumps(analysis, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f'Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges, {len(communities)} communities')

    # Step 4.5
    summary = diagnose_extraction(extraction, directed=False, root='.')
    print(format_diagnostic_report(summary))
    flags = [f'{summary[k]} {label}' for k, label in (
        ('dangling_endpoint_edges', 'dangling-endpoint edges'),
        ('missing_endpoint_edges', 'missing-endpoint edges'),
        ('self_loop_edges', 'self-loop edges'),
        ('directed_same_endpoint_collapsed_edges', 'collapsed (directed) edges'),
        ('undirected_same_endpoint_collapsed_edges', 'collapsed (undirected) edges'),
    ) if summary.get(k, 0)]
    print('GRAPH HEALTH WARNING: ' + '; '.join(flags) + ' - graph may be incomplete/corrupt.' if flags else 'Graph health: OK (no dangling/missing/collapsed edges).')

if __name__ == '__main__':
    main()
