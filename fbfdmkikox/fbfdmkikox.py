"""
1.Template for generating SWOT analysis by uploading a business document.
2.Process the document in chunks as INPUT to ensure comprehensive analysis..
2.Refine the prompts by adding or removing examples and setting word limits to enhance accuracy..
3.Designed to work seamlessly with Llama models for generating precise SWOT insights.
4.Aims to provide accurate SWOT analysis to help organizations identify important business insights.
"""
prompt= f"""
<|begin_of_text|><|start_header_id|>system<|end_header_id|>
A SWOT analysis is a valuable framework that helps you evaluate your business from different angles,
discover new ways to grow and improve, and make smarter decisions. The analysis can guide you in using your strengths to stand out,
addressing weaknesses before they hurt, seizing new opportunities, and preparing for potential threats. 
This summary will provide a concise overview followed by a detailed analysis of each category.
Please give the output in Japanese only.
Input: {text}
Rules:
Remain true to the context provided by the original value and enhance the description.
Be accurate and do not introduce factual inaccuracies or assumptions that are not supported by the input data.
Provide a comprehensive understanding, making sure the description is coherent, detailed, and creatively fulfilling.
Provide a 2-3 line summary that impacts the business.
Follow the provided template for each category (Strength, Weakness, Opportunity, Threat) and give the output in the specified format.
Example Templates:
Summary
技術力と品質管理が強みである一方、高コストや物流課題が弱みとなっている。グリーンテクノロ ジーへの移行や海外市場拡大が機会であり、
競争激化や法規制変化が脅威として存在する。これらの 要因を考慮し、新技術の採用や市場戦略の再評価が重要である。
👍 STRENGTH
    技術力: 当社は革新的な技術を持ち、製品やサービスの品質を高めるための先端技術を開発している。
    品質管理: 品質管理システムが徹底しており、顧客満足度を高めるために高品質な製品を提供できる。
    ブランド認知度: 当社のブランドは業界内で高く評価され、顧客からの信頼が厚い。
👎 WEAKNESS
    高コスト: 製品の生産や研究開発に関連するコストが高く、競争力を弱める要因となっている。
    ロジスティクスの課題: 物流や供給チェーンに関する問題があり、効率性が低下している。
    新規市場への進出の遅れ: 新興市場や成長市場への参入が遅れており、市場シェアの拡大に課題がある。
💡 OPPORTUNITY
    グリーンテクノロジーへの移行: 環境に配慮した製品やサービスの需要が高まっており、グリーンテクノロジーへの注力が新たな市場を開拓する機会となる。
    新技術の採用: 人工知能やIoTなどの新技術を活用して、製品の性能向上や生産プロセスの効率化を図ることが可能。
⛔️ THREAT
    競争の激化: 競合他社の技術革新や価格競争が激しく、市場シェアの維持が難しい状況にある。
    法規制の変化: 環境規制や安全規制の厳格化が進行しており、これに適合するための投資や対応が必要となる。
    供給チェーンの脆弱性: 物流や原材料の供給に関する問題が発生しやすく、これが製品供給に影響を与える可能性がある。
Now observe the above example template and provide the output by following the rules in the above format.
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
    return prompt
Footer