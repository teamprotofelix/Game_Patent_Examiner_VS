export const WEAPONS={
 blade:{id:'blade',name:'구성대비 블레이드',icon:'blade',desc:'주변 적을 강력하게 베며 넉백.',base:21,interval:.75,range:135,color:'#62eaff'},
 laser:{id:'laser',name:'신규성 레이저',icon:'laser',desc:'가장 가까운 적을 관통하는 정밀 광선.',base:18,interval:1.25,range:500,color:'#62baff'},
 chain:{id:'chain',name:'진보성 체인',icon:'chain',desc:'적 사이를 번개처럼 도약하는 연쇄 공격.',base:19,interval:1.65,range:300,color:'#ffcc72'},
 shield:{id:'shield',name:'명확성 실드',icon:'shield',desc:'주기적으로 주변 적을 밀어내는 충격파.',base:16,interval:2.5,range:120,color:'#7bf5cc'},
 drone:{id:'drone',name:'인용문헌 드론',icon:'drone',desc:'동행 드론이 유도탄을 연사.',base:13,interval:.95,range:410,color:'#aba1ff'},
 markush:{id:'markush',name:'마쿠시 마법진',icon:'markush',desc:'원형 반응장에서 지속 광역 피해.',base:12,interval:2.1,range:170,color:'#e998ff'}
};
export const EVOLUTIONS=[
 {id:'storm',name:'구성대비 폭풍',requires:['blade','laser'],desc:'광검과 레이저가 동시 회전하며 연속 타격.'},
 {id:'barrage',name:'선행기술 연쇄 포격',requires:['drone','chain'],desc:'추적 드론이 전격을 확산.'},
 {id:'barrier',name:'심사품질 결계',requires:['markush','shield'],desc:'광역 반응장과 방벽이 융합.'}
];
export const STATS={speed:{name:'기동 알고리즘',icon:'speed',desc:'이동 속도 +12%'},power:{name:'심사 정확도',icon:'power',desc:'모든 무기 피해 +14%'},health:{name:'품질 방어력',icon:'heart',desc:'최대 체력 +25, 즉시 회복'},area:{name:'광역 판단',icon:'range',desc:'공격 범위 +12%'},cooldown:{name:'고속 검토',icon:'crit',desc:'무기 재사용 대기 -8%'},projectile:{name:'복수 구성 분석',icon:'projectile',desc:'일부 투사체 추가 +1'},magnet:{name:'문헌 자동 수집',icon:'xp',desc:'경험치 흡수 범위 +45%'},dash:{name:'긴급 보정 회피',icon:'dash',desc:'대시 대기시간 -15%'},regen:{name:'집중력 회복',icon:'heal',desc:'6초마다 체력 회복 +2'},crit:{name:'핵심 구성 포착',icon:'crit',desc:'치명타 확률 +6%'}};
