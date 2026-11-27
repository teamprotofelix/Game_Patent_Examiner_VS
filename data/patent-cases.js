// No invented statute numbers. Hypothetical narrowly scoped exam reasoning, source and review state are explicit.
export const PATENT_CASES=[
 {id:'novelty-components',topic:'신규성',status:'학습용 예시 · 전문가 감수 전',source:{title:'지식재산처 특허·실용신안 심사기준 (2026.03.12)',url:'https://www.moip.go.kr/ko/kpoContentView.do?menuCd=SCD0200146'},
  prompt:'청구항은 A+B+C를 필수 구성으로 기재합니다. 공개 시점이 적절한 인용문헌 1에는 A+B만 명확히 개시되어 있고 C는 개시되어 있지 않습니다. 이 문헌 하나만을 이유로 신규성이 없다고 판단할 수 있을까요?',
  options:['이 문헌만으로는 신규성 부정이 곤란합니다.','A+B가 있으니 신규성이 없습니다.','인용문헌 2를 임의로 조합하면 언제나 신규성이 없습니다.'],correct:0,
  explanation:'신규성은 원칙적으로 개별 선행기술에 청구발명의 모든 구성이 개시되는지 살핍니다. C가 확인되지 않는다는 전제에서 문헌 1만으로 신규성 결여를 단정하기 어렵습니다. 진보성 판단은 별도입니다.'},
 {id:'clarity-context',topic:'명확성',status:'학습용 예시 · 전문가 감수 전',source:{title:'지식재산처 특허·실용신안 심사기준 (2026.03.12)',url:'https://www.moip.go.kr/ko/kpoContentView.do?menuCd=SCD0200146'},
  prompt:'청구항에 특정 용어가 나옵니다. 심사관이 용어만 떼어 보니 다소 낯설지만, 발명의 설명에 측정 방법과 기술적 정의가 구체적으로 나옵니다. 어떤 검토가 먼저일까요?',
  options:['용어가 낯설면 자동으로 기재불비입니다.','청구항과 발명의 설명, 통상의 기술 지식을 함께 살핍니다.','정의가 있어도 검토할 필요는 없습니다.'],correct:1,
  explanation:'명확성은 해당 용어의 단독 인상만이 아니라 청구항 전체, 발명의 설명 및 기술상식을 포함해 판단해야 합니다. 구체적 사정에 따라 결론이 달라집니다.'},
 {id:'amendment-new',topic:'보정',status:'학습용 예시 · 전문가 감수 전',source:{title:'지식재산처 특허·실용신안 심사기준 (2026.03.12)',url:'https://www.moip.go.kr/ko/kpoContentView.do?menuCd=SCD0200146'},
  prompt:'원래 출원서류에는 나타나지 않는 새로운 기술적 구성 D를 보정서로 추가하려 합니다. 심사관이 우선 확인할 것은 무엇일까요?',
  options:['D의 신규사항 여부와 최초 기재 근거를 확인합니다.','보정이므로 내용에 관계없이 항상 허용합니다.','기술내용 검토 없이 무조건 자동 거절합니다.'],correct:0,
  explanation:'보정은 최초 명세서 등에 기재된 사항의 범위를 벗어나는지 등 구체적 요건과 시기를 따져야 합니다. 이것만으로 최종 심사결론을 대신하지는 않습니다.'}
];
