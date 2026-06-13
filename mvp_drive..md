# 빠른 MVP 출시와 복잡한 결제 및 정산 시스템의 확장을 위한 소프트웨어 아키텍처 기술 전략

## 1. 서론: 신속한 시장 검증과 금융 무결성 확보의 역설적 요구

현대의 소프트웨어 엔지니어링 생태계에서 '최소 기능 제품(MVP, Minimum Viable Product)'의 빠른 출시는 비즈니스의 생존과 직결된 핵심 전략이다. 시장의 피드백을 신속하게 수용하고 프로덕트 마켓 핏(Product-Market Fit)을 검증하기 위해 개발팀은 초기 개발 속도를 극대화하라는 압박을 받는다. 그러나 해당 비즈니스가 핀테크, 커머스 마켓플레이스, 혹은 다자간 정산을 동반하는 플랫폼 비즈니스라면, 이러한 '속도 지상주의'는 치명적인 기술적 부채를 잉태하게 된다.

비즈니스 아이디어의 검증은 신속해야 하지만, 그 기저에서 자금의 흐름을 통제하는 결제 및 정산 시스템은 무결성, 보안, 그리고 고도로 복잡한 금융 규제 기준을 완벽하게 충족해야 하기 때문이다. 대다수의 소프트웨어 프로젝트가 기능적 요구사항(Feature wishlist)에서 출발하는 것과 달리, 금융과 관련된 플랫폼의 개발은 관할권의 규제 지도를 그리는 것에서부터 시작되어야 한다1. 고객의 잔고를 단순한 데이터베이스 테이블의 단일 정수(Integer) 값으로 관리하거나, 외부 결제대행사(PG)의 응답에 시스템의 핵심 로직이 강하게 결합되도록 설계하는 초기 타협안은 결국 시스템의 신뢰성을 근본적으로 무너뜨린다2. 환불, 부분 취소, 차지백(Chargeback), 복합 수수료 정산과 같은 엣지 케이스(Edge case)가 발생하는 순간, 강결합된 아키텍처와 단일 항목 기반의 원장은 그 한계를 여실히 드러낸다2.

본 보고서는 "빠른 MVP 출시"라는 비즈니스적 요구사항과 "안전하고 복잡한 결제 및 정산 시스템 구축을 위한 공간 확보"라는 아키텍처적 요구사항을 동시에 충족하기 위한 심층적인 기술 및 운영 전략을 제시한다. 이를 위해 시스템의 거시적 구조를 결정하는 모듈러 모놀리스(Modular Monolith)와 헥사고날 아키텍처(Hexagonal Architecture)의 도입 타당성을 분석하고, 자금 흐름의 수학적 무결성을 보장하는 복식부기(Double-entry) 기반의 추가 전용(Append-only) 원장 시스템의 설계 방안을 논의한다. 더불어, 토스페이먼츠(Toss Payments)와 포트원(PortOne)을 필두로 한 국내 주요 결제 및 정산 API의 연동 전략과 최근 전자금융거래법(이하 전금법) 개정에 따른 컴플라이언스 대응 방안을 종합적으로 고찰한다.

## 2. 규제 환경과 컴플라이언스: 아키텍처 설계의 선제 조건

결제 및 정산 시스템을 설계하기에 앞서, 개발팀은 대상 시장의 규제 환경을 아키텍처의 핵심 기둥으로 삼아야 한다. 규제 준수(Compliance)는 단순히 런칭 이후에 덧붙이는 기능이 아니라, 시스템의 데이터 모델과 권한 흐름을 결정짓는 직접적인 성장 레버(Growth lever)로 작용한다1.

### 2.1. 글로벌 금융 규제의 기술적 함의

글로벌 시장을 목표로 하는 플랫폼의 경우, 각 지역의 파편화된 규제를 시스템 내에 추상화해야 한다. 유럽 및 영국의 경우 PSD2 및 PSD3 지침, 오픈 뱅킹 규정, 개인정보보호규정(GDPR) 등이 적용되며, 카드 결제 데이터를 직접 처리할 경우 전 세계 공통으로 지불 카드 산업 데이터 보안 표준(PCI DSS)을 준수해야 한다1. 미국 시장의 경우 주(State) 단위의 상이한 규제와 소비자금융보호국(CFPB), 금융범죄단속네트워크(FinCEN)의 연방 감독을 동시에 받아야 하며, 암호화폐와 같은 디지털 자산을 취급할 경우 미카(MiCA) 및 트래블 룰(Travel Rule)이 추가로 요구된다1.

이러한 규제들은 필연적으로 감사 추적(Audit trails), 데이터 레지던시(Data residency), 신원 확인(KYC), 자금 세탁 방지(AML)를 위한 거래 모니터링 등의 기술적 구현을 강제한다1. 따라서 MVP 단계에서부터 개인 식별 정보(PII)의 격리 보관과 모든 트랜잭션의 불변적 기록(Immutable logging)이 가능한 구조를 확보해야 한다.

### 2.2. 국내 전자금융거래법 개정과 대규모 미정산 사태의 교훈

한국 시장에서는 최근 발생한 티몬·위메프(이하 티메프) 대규모 미정산 사태가 핀테크 및 이커머스 플랫폼의 시스템 아키텍처와 비즈니스 모델에 전례 없는 충격을 주었다. 해당 사태는 오픈마켓 사업자가 파트너에게 정산해 주어야 할 판매 대금과 자사의 운영 자금을 엄격히 분리하지 않고 혼용하여 사용한 데서 비롯되었다5. 이에 대응하여 한국 금융 당국은 전자금융거래법 및 대규모유통업법을 전면 개정하여 플랫폼 사업자의 자금 유용을 원천 차단하는 강력한 규제를 도입했다5.

개정된 규제의 핵심은 정산 자금의 100% 별도 관리 의무화와 정산 주기의 대폭 단축이다. 전자지급결제대행업(PG) 및 일정 규모 이상의 플랫폼은 수취한 결제 대금 전액을 에스크로(Escrow), 신탁, 예치, 또는 지급보증보험의 형태로 외부 기관에 분리 보관해야 한다5. 이렇게 분리된 자금은 압류나 상계가 금지되며, 파트너(판매자)가 우선 변제권을 가지게 된다7. 또한, 정산 기한 역시 구매 확정일 또는 결제일로부터 최대 40일 이내로 강제되었으며, 법안 시행 후 단계적으로 30일, 최종 20일까지 단축될 예정이다6. 정산 기한을 초과할 경우 플랫폼은 파트너에게 법정 지연 이자를 지급해야 할 의무가 발생한다7.

이러한 법적 요구사항은 시스템 설계에 즉각적인 변화를 요구한다. 개발자는 내부 원장 시스템(Ledger)에서 '자산의 색칠(Assets Coloring)' 기법을 도입하여, 통합된 은행 계좌 내에서도 플랫폼의 수익(수수료) 계정과 파트너에게 귀속될 대기 자금(Pending Escrow) 계정을 논리적으로 완벽히 분리해야 한다4. 시스템은 회계적으로 이 두 자산이 섞이거나 담보로 잡히는 것을 데이터베이스 레벨에서 차단해야 한다4.

### 2.3. PG업 등록 면제 조건과 지급대행 인프라의 전략적 활용

스타트업이나 초기 플랫폼이 개정된 전자금융거래법상 PG업자로 직접 등록하기 위해서는 분기별 결제대행 규모에 따라 최대 30억 원 이상의 자본금 요건과 엄격한 재무건전성 기준을 충족해야 한다11. 이는 MVP를 준비하는 조직에게 사실상 불가능한 진입 장벽이다.

그러나 금융 당국은 백화점, 프랜차이즈 등 유통업계의 내부 정산 업무나, 외부 전문 PG사의 시스템을 활용하여 플랫폼이 자금 이동에 직접 관여하지 않는 구조를 채택할 경우 PG업 등록 의무를 면제하는 비조치의견서 및 법령 해석을 제공하고 있다13. 따라서 초기 플랫폼은 자사 시스템에 결제 대금을 직접 수용하는 아키텍처를 피하고, 토스페이먼츠나 포트원과 같은 검증된 인프라의 '지급대행(Payout)' API나 '서브 가맹점 정산' 모델을 활용하여 원천 PG사가 파트너의 계좌로 직접 송금하도록 유도하는 전략이 필수적이다13.

## 3. 구조적 토대: 마이크로서비스의 함정과 모듈러 모놀리스

규제적 요구사항을 만족하면서도 MVP의 신속한 출시를 달성하기 위해 가장 먼저 결정해야 할 것은 소프트웨어의 물리적 배포 및 논리적 분리 단위다. 무한한 확장성을 내세우며 마이크로서비스 아키텍처(MSA)를 초기부터 채택하려는 시도가 잦으나, 이는 종종 프로젝트의 지연과 운영 붕괴로 이어진다.

### 3.1. 분산 모놀리스의 위험성

초기 비즈니스 환경에서는 도메인의 경계가 아직 명확하게 확립되지 않은 상태다17. 이러한 상황에서 애플리케이션을 무리하게 물리적 서비스로 쪼개게 되면, 시스템은 '분산 모놀리스(Distributed Monolith)'라는 최악의 안티 패턴으로 전락한다17. 분산 모놀리스 환경에서는 단순한 결제 요청 하나를 처리하기 위해 서비스들이 네트워크를 통해 수많은 동기식 HTTP 호출을 주고받아야 하며, 이는 심각한 네트워크 지연(Latency)과 직렬화 오버헤드를 유발한다17.

무엇보다 금융 데이터의 무결성을 보장하기 위한 분산 트랜잭션 처리가 극도로 어려워진다. 단일 데이터베이스 환경에서는 손쉽게 구현 가능한 ACID 트랜잭션이, 분산 환경에서는 사가(Saga) 패턴이나 2단계 커밋(2PC)과 같은 고도의 오케스트레이션 로직을 강제한다17. 또한, 인프라스트럭처 측면에서도 쿠버네티스(Kubernetes), 서비스 디스커버리, 메시지 브로커, 분산 트레이싱 등 소규모 팀이 감당하기 힘든 운영 복잡성이 부과되며, 결과적으로 기능 개발보다 인프라 유지보수에 더 많은 시간을 쏟게 된다17.

### 3.2. 모듈러 모놀리스의 구조와 도메인 주도 설계(DDD)의 결합

분산 환경의 한계를 극복하기 위한 최적의 대안은 애플리케이션을 단일 단위로 배포하되, 코드 내부는 엄격한 경계를 가진 비즈니스 도메인 모듈로 구성하는 '모듈러 모놀리스(Modular Monolith)'를 도입하는 것이다17. 모놀리스가 곧 스파게티 코드를 의미한다는 오해와 달리, 현대적인 도메인 주도 설계(DDD)는 본래 모놀리식 시스템에 명확성, 유연성, 비즈니스 정렬을 부여하기 위해 고안된 패러다임이다17.

규모가 큰 조직에서도 모듈러 모놀리스의 효용성은 입증되고 있다. 미국의 급여 처리 플랫폼 기업 CheckHQ는 전통적인 계층형 모놀리스나 마이크로서비스 대신 모듈러 모놀리스를 채택하여 급여 정산 시스템을 안정적으로 스케일링했다20. 이들의 시스템 구조를 살펴보면, Django 기반 단일 코드베이스 내에 companies(기업 및 근로자 수명주기 관리), payments(결제 처리), payrolls(급여 구성 및 처리), risk(사기 탐지 및 신용 평가) 등의 하위 도메인이 각각 독립된 애플리케이션(모듈)으로 분리되어 있다20.

모듈러 모놀리스가 진정한 확장성을 가지려면 다음의 엄격한 원칙들이 시스템 내에 강제되어야 한다.

* **데이터베이스 모델의 사유화 및 외래 키 금지:** 각 모듈(하위 도메인)의 데이터와 스키마는 철저히 해당 모듈에 종속되어야 한다. 서로 다른 모듈 간의 데이터베이스 외래 키(Foreign Key) 참조는 엄격히 금지된다20. 급여 모듈의 데이터베이스 테이블이 결제 모듈의 데이터베이스 테이블을 직접 조인(Join)하게 되면 눈에 보이지 않는 데이터베이스 계층의 강결합이 발생하기 때문이다20.
* **명시적 인터페이스와 이벤트 기반 통신:** 모듈 간의 통신은 오직 JSON 직렬화가 가능한 데이터 객체와 명시적으로 문서화된 서비스 컨트랙트(API 인터페이스)를 통해서만 이루어져야 한다19. 나아가 내부 메시지 브로커나 이벤트 버스를 활용하여 도메인 이벤트(Domain Events)를 발행하고 구독하는 방식을 취해야 한다. 예를 들어, 결제 모듈에서 '결제 완료(PaymentCompleted)' 이벤트가 발생하면, 정산 모듈이 이를 비동기적으로 수신하여 정산원장을 업데이트하는 구조를 취함으로써 모듈 간의 결합도를 마이크로서비스 수준으로 낮출 수 있다19.
* **테스트 격리 및 의존성 시각화:** 자동화된 린팅(Linting) 도구를 도입하여 특정 모듈이 허용되지 않은 다른 모듈의 내부 클래스를 직접 임포트(Import)하는 것을 차단하고, 변경된 애플리케이션 모듈에 해당하는 테스트만 실행하여 CI/CD 파이프라인의 속도를 비약적으로 향상시킬 수 있다20.

### 3.3. 스트랭글러 피그 패턴을 통한 점진적 전환

NestJS와 같이 구조화된 프레임워크를 사용할 경우, MVP 단계에서 구축한 모듈 구조(예: @Module({ imports: [PaymentsModule, OrdersModule] }))를 향후 비즈니스가 급성장했을 때 그대로 활용하여 마이크로서비스로 전환할 수 있다17. 특정 모듈에 부하가 집중되거나 별도의 개발팀이 신설될 경우, 시스템 전체를 멈추지 않고 해당 모듈만 점진적으로 독립 서비스로 추출해 나가는 '스트랭글러 피그 패턴(Strangler Fig pattern)'을 적용하는 것이 가장 안전한 기술 진화 전략이다17.

## 4. 외부 의존성 통제: 헥사고날 아키텍처 (포트와 어댑터)

모듈러 모놀리스가 시스템 내부의 하위 도메인 간 결합도를 낮추기 위한 아키텍처라면, 헥사고날 아키텍처(Hexagonal Architecture), 일명 '포트와 어댑터(Ports and Adapters)' 패턴은 비즈니스 핵심 로직을 외부 시스템 및 인프라스트럭처의 변동성으로부터 철저히 격리하기 위한 설계 패러다임이다21.

결제 및 정산 시스템은 필연적으로 토스페이먼츠, 포트원, 은행의 오픈뱅킹 망, 이메일 전송 서비스(SendGrid, AWS SES) 등 수많은 외부 인프라와 통신해야 한다24. 만약 MVP 단계에서 비즈니스 로직 코드베이스 내부에 특정 PG사의 API 호출 방식이나 응답 포맷이 직접 하드코딩된다면, 향후 다른 국가로 진출하거나 수수료 절감을 위해 복수의 PG사를 라우팅해야 할 때 시스템 전체를 재작성해야 하는 기술 부채에 직면하게 된다22.

### 4.1. 의존성 역전과 도메인의 안식처

2005년 알리스테어 코오번(Alistair Cockburn) 박사가 제안한 이 패턴의 핵심 아이디어는 애플리케이션의 핵심 비즈니스 로직(도메인 모델)을 중앙의 헥사곤(Hexagon) 내부에 배치하고, 이를 어떠한 외부 기술이나 프레임워크에도 의존하지 않도록 순수한 형태로 유지하는 것이다22. 외부 세계와의 모든 소통은 오직 인터페이스로 정의된 '포트(Ports)'를 통해서만 이루어진다21.

* **포트 (Ports):** 시스템이 할 수 있는 일과 외부로부터 필요한 정보를 정의하는 추상적인 계약(Contract)이다. 여기에는 어떠한 HTTP 개념이나 특정 SDK의 이름도 포함되지 않는다21.
  + *주도하는 포트(Primary/Driving Ports):* 사용자 상호작용이나 외부 API 요청이 애플리케이션으로 들어오는 진입점이다. 예를 들어 placeOrder(OrderDetails)와 같은 형태를 가진다21.
  + *주도되는 포트(Secondary/Driven Ports):* 핵심 로직이 데이터베이스나 PG사 등 외부 시스템에 의존해야 할 때 밖으로 내보내는 요청의 인터페이스다. 비즈니스의 언어로 작성되며, "ChargeCard", "SendEmail"과 같이 행위에 집중한다21.
* **어댑터 (Adapters):** 추상적인 포트의 규격을 외부 시스템의 구체적 현실로 번역하는 플러그다24.
  + *주도하는 어댑터(Primary/Driving Adapters):* HTTP 요청을 파싱하여 주도하는 포트를 호출하는 웹 컨트롤러(예: WebOrderController)나 CLI 핸들러가 이에 속한다21.
  + *주도되는 어댑터(Secondary/Driven Adapters):* 주도되는 포트의 인터페이스를 실제로 구현하여 외부 시스템과 직접 통신하는 클래스다. 예를 들어 PaymentGatewayPort 인터페이스를 구현하는 TossPaymentsAdapter나 PortOneAdapter가 이에 해당한다21.

### 4.2. 런타임 다형성과 레지스트리의 역할

이러한 의존성 역전(Dependency Inversion)의 핵심은 화살표의 방향이 항상 외부(어댑터)에서 내부(비즈니스 로직과 포트)를 향해야 한다는 점에 있다24. 즉, 프로젝트 디렉토리 구조상 핵심 비즈니스 로직이 위치한 파일들은 포트를 임포트(Import)할 수는 있지만, 어댑터의 구체적인 구현체 파일은 절대 임포트해서는 안 된다24.

어떤 어댑터를 포트에 연결할 것인지는 오직 '레지스트리(Registry)' 또는 '의존성 주입(IoC) 컨테이너'만이 알고 있으며, 런타임에 결정된다21. 이를 비유하자면, 벽면의 전기 콘센트(포트)에 어떠한 브랜드의 충전기 플러그(어댑터)를 꽂더라도 전기를 사용할 수 있는 것과 동일한 이치다24.

이러한 설계는 MVP 개발 환경에서 압도적인 장점을 제공한다. 초기 개발 단계에서는 실제 은행 시스템이나 PG사의 승인을 기다릴 필요 없이, 포트 인터페이스를 구현한 MockPaymentAdapter를 생성하여 핵심 정산 로직의 모든 케이스를 완벽하게 유닛 테스트할 수 있다22. 이후 비즈니스가 확장되어 새로운 결제 사업자를 추가하더라도, 핵심 코드는 단 한 줄도 변경하지 않은 채 새로운 어댑터 클래스를 작성하고 레지스트리만 업데이트하면 즉각적인 전환이 완료된다23.

## 5. 코어 엔진: 이중 입력(Double-Entry) 기반 추가 전용 원장 시스템

마이크로서비스의 함정을 피해 모듈러 모놀리스를 구축하고 헥사고날 아키텍처로 외부 의존성을 차단했다면, 가장 핵심적인 과제인 '원장(Ledger) 데이터베이스 모델링'을 설계해야 한다.

### 5.1. 상태 기반 설계의 한계와 복식부기의 원리

수많은 개발자들이 사용자나 기업의 잔고를 관리할 때, 데이터베이스 내에 balance 컬럼을 생성하고 이벤트가 발생할 때마다 해당 값을 UPDATE 하는 상태 기반(State-based) 접근을 취한다2. 이 방식은 구현이 극도로 단순하여 MVP에 매력적으로 보이지만, 금융 애플리케이션에서는 시한폭탄과 다름없다. 단일 항목 수정 방식은 자금의 출처와 목적지를 명확히 연결하지 못하며, 어떠한 과정을 거쳐 현재 잔고에 이르렀는지를 증명할 감사 추적(Audit trail) 능력이 전혀 없다2. 더욱이 병렬 트랜잭션이 다수 발생하는 환경에서는 데이터베이스 락(Lock) 경합이나 레이스 컨디션으로 인해 잔고가 증발하거나 무단 증액되는 치명적 무결성 오류가 발생하기 쉽다27.

이러한 문제를 원천적으로 해결하는 것이 수백 년 전부터 인류의 상업 생태계를 지탱해 온 '복식부기(Double-entry bookkeeping)' 개념의 도입이다3. 복식부기 원장의 핵심 철학은 시스템 내에서 발생하는 모든 자금 이동을 동일한 금액의 '차변(Debit)'과 '대변(Credit)' 쌍으로 동시에 기록하는 데 있다2.

결제 수단, 서비스 수수료, 미정산 보관금, 파트너의 가상 지갑 등을 모두 추상적인 '계정(Account)'으로 모델링하여 계정과목표(Chart of Accounts, CoA)를 구성한다28. 사용자의 결제 금액이 플랫폼으로 유입될 때, 외부 세계를 대표하는 가상의 결제 계정(Settlement Account)에서 대변 항목이 생성되고, 플랫폼 내 사용자의 지갑 계정에서 동액의 차변 항목이 생성된다2. 복식부기 시스템의 모든 트랜잭션은 단일 데이터베이스 커밋 내에서 반드시 합계가 '0'이 되도록 제약되며, 이는 자금 누수와 오차를 수학적으로 불가능하게 만드는 방어 기제다2.

### 5.2. 추가 전용(Append-only) 아키텍처와 암호학적 무결성

원장 시스템에서 데이터는 물리적 세계의 시간의 흐름과 같아야 한다. 어떠한 경우에도 한 번 기록된 전표(Journal)는 수정(Update)되거나 삭제(Delete)되어서는 안 된다3. 오직 새로운 이벤트를 로그 끝에 덧붙이는 '추가 전용(Append-only)' 연산만이 허용된다2. 오류가 발생한 경우 데이터를 지우는 대신, 기존 트랜잭션을 역산하여 상쇄하는 반대 방향의 수정 전표(Reversal entry)를 기입하여 오기입 자체도 히스토리로 보존해야 한다27.

성능 및 무결성을 보장하기 위해, 시스템 설계 시 다음의 기법들을 데이터베이스 계층에 적용해야 한다.

* **DB 레벨의 엄격한 제약(Constraints) 설정:** PostgreSQL 등 RDBMS를 사용할 경우, check\_single\_side와 같은 CHECK 제약 조건을 통해 각 기입 로우가 차변 혹은 대변 중 반드시 하나만의 속성을 갖도록 데이터베이스 레벨에서 강제한다2. 또한 트랜잭션 종류(예: 입금, 송금, 환불)를 데이터베이스 ENUM 타입으로 지정하여 애플리케이션 코드의 버그로 인한 잘못된 타입 기입을 원천 차단한다2.
* **암호학적 해시 체이닝(Cryptographic Hash Chaining):** 극도의 무결성이 요구되는 인프라에서는 각 원장 기록이 자신의 데이터뿐만 아니라 직전 기록의 암호학적 해시(SHA-256 등)값을 포함하도록 설계한다27. 이는 블록체인의 작동 원리와 유사하며, 단 하나의 데이터라도 악의적으로 변조될 경우 전체 체인의 무결성이 파괴되므로 즉각적인 감사 및 위변조 탐지가 가능해진다26.
* **멱등성(Idempotency) 보장과 동시성 제어:** 분산 시스템의 네트워크 불안정성으로 인해 클라이언트의 결제 승인 요청이 타임아웃되어 재시도될 경우, 자금이 중복으로 이동할 위험이 있다4. 이를 방지하기 위해 각각의 트랜잭션은 클라이언트가 생성한 멱등성 키(Idempotency Key, 주로 UUID 또는 시간순 정렬이 가능한 ULID 형태)를 참조 ID로 포함해야 하며, DB는 이를 유니크 제약(Unique Constraint)으로 차단해야 한다2. 아울러 동시 다발적인 구매 요청 시 발생하는 계정 락(Lock) 병목 현상을 해소하기 위해, 동적 로우 파티셔닝(Dynamic row partitioning) 등의 잠금 없는(Lock-Free) 동시성 처리 기법이 요구된다27.

### 5.3. 오픈소스 기반 PostgreSQL 원장 적용 (pgledger 및 DoubleEntryLedger)

초기 스타트업이 이토록 정교한 복식부기 및 해시 체이닝 원장을 처음부터 직접 구축하기는 어렵다. 최근에는 비즈니스 로직과 원장 로직을 분리하여, 데이터베이스 계층 자체에서 원장의 무결성을 책임지게 하는 오픈소스 솔루션들이 주목받고 있다.

순수 PostgreSQL로 구현된 pgledger나 Elixir/PostgreSQL 기반의 DoubleEntryLedger가 대표적인 사례다29. 이 시스템들은 원장의 핵심 로직을 애플리케이션 프레임워크가 아닌 PostgreSQL의 함수, 트리거, 제약 조건 내부에 하드코딩한다29. 개발자는 단순히 SQL 함수(예: pgledger\_create\_transfer())를 호출함으로써 동일한 데이터베이스 트랜잭션 안에서 차변과 대변의 이중 입력을 원자적으로(Atomically) 완료할 수 있다29. 방대해진 추가 전용 이벤트 스트림에서 특정 계정의 현재 잔고를 빠르게 조회하기 위해 머티리얼라이즈드 뷰(Materialized Views)를 캐시로 사용하며, 데이터가 삽입될 때 백그라운드 트리거를 통해 잔고를 실시간 재계산하는 방식을 통해 읽기 성능의 병목을 해결한다30. 또한 Elixir 생태계의 DoubleEntryLedger와 같이 Oban 등 백그라운드 작업 큐(Job queue)를 연동하여 낙관적 동시성 제어(OCC)와 이벤트 처리 재시도를 자동으로 스케줄링하는 고도화된 기능도 제공된다35.

### 5.4. 잔고의 다층적 이해: 원장 잔고, 가용 잔고, 대기 잔고

기술적 구현을 넘어 도메인 전문가로서 주의해야 할 점은 시스템 내에서 관리되는 '잔고(Balance)'의 개념적 분리다. 시스템의 버그는 종종 개발자가 서로 다른 맥락의 잔고를 혼용할 때 발생한다4. 핀테크 시스템은 하나의 계정에 대해 최소 세 가지 잔고 상태를 유지하고 추적해야 한다4.

1. **원장 잔고 (Ledger Balance):** 전통적 금융권 배치 처리의 결과이든 실시간 누적합이든, 정식으로 승인되고 매입이 확정되어 완전히 회계적으로 결산된 트랜잭션들의 총합이다4.
2. **가용 잔고 (Available Balance):** 원장 잔고에서 고객이 향후 사용하기 위해 시스템에 의해 홀딩된 금액(Holdings)이나 권한 부여(Authorization)가 진행 중인 금액을 제외한, 현재 즉시 출금하거나 사용할 수 있는 실질 금액이다4.
3. **대기 잔고 (Pending Balance):** 외부 PG사에서 승인은 되었으나 아직 대금이 플랫폼 계좌로 입금되지 않아 정산 대기 중인 상태의 자금 흐름을 뜻한다4.

마켓플레이스에서 특정 판매자의 수익을 정산해 줄 때 가용 잔고와 대기 잔고의 조건을 명확히 구분하여 처리하지 않으면, 환불이나 차지백 발생 시 플랫폼이 손실을 떠안게 되는 심각한 재무 사고로 이어진다4.

## 6. 결제 및 정산 API 연동: 포트원과 토스페이먼츠의 입체적 비교

견고한 원장 엔진과 헥사고날 아키텍처 기반의 인터페이스를 갖추었다면, 이제 구체적인 주도되는 어댑터(Driven Adapter)를 외부 결제대행(PG) 인프라에 연결할 차례다. 한국 시장에서 개발자 친화성과 강력한 생태계를 자랑하는 토스페이먼츠(Toss Payments)와, 복잡한 파트너 정산 및 세무 자동화에 특화된 포트원(PortOne)의 특성을 명확히 비교하고 각자의 전략적 이점을 아키텍처에 반영해야 한다.

### 6.1. 토스페이먼츠: 압도적 개발자 경험(DX)과 지급대행 인프라

토스페이먼츠는 전통적인 한국 PG 산업의 낡은 레거시를 현대적인 RESTful API 형태로 재설계하여 압도적인 수준의 개발자 경험을 제공한다36.

토스페이먼츠의 오픈 API 설계는 기능 중심이 아닌 자원(Resource)을 중심으로 한 리소스 지향 설계(Resource-Oriented Design) 원칙을 철저히 준수하여 응답 포맷이 고도로 예측 가능하다36. 실시간 응답이 필요한 로직은 API를 통해, 비동기 처리가 필요한 로직(예: 결제 완료 후 계좌 입금 확인)은 웹훅(Webhook)을 통해 처리하며, 두 인터페이스 모두 동일한 리소스 객체 형태를 반환하여 데이터 파싱 로직의 재사용성을 극대화했다36.

가장 눈여겨볼 기능은 오픈마켓 정산용 '지급대행(Payouts)' API다.

* **셀러 온보딩 및 KYC:** 플랫폼은 입점 셀러를 POST /v2/sellers API를 통해 토스페이먼츠 시스템에 직접 등록하며, 이 과정에서 예금주 일치 여부와 유효성을 즉각 검증한다16. 특정 셀러에 대한 지급 대행 금액이 일주일 내 천만 원을 초과할 경우 셀러 상태가 KYC\_REQUIRED로 변경되어, 자금 세탁 방지 및 본인 인증 절차를 통과할 때까지 자금 지급이 시스템 레벨에서 자동 블락(Block)된다37.
* **안정적인 정산 조회:** 지급일(DUE)과 거래 승인일(SETTLE)을 구분하여 정산 상세 내역을 조회할 수 있으며, 1,000건 단위의 데이터 페이지를 nextCursor 방식의 페이징으로 제공하여 서버 간 동기화 누락을 방지한다38.
* **직관적인 지급 옵션:** 잔액 조회(Balance)를 거쳐 가용 금액(availableAmount) 한도 내에서 지급대행을 요청하며, 요청 당일 지급되는 바로지급(EXPRESS)과 미래 날짜를 지정하는 예약지급(SCHEDULED) 옵션을 제공한다16.
* **보안 환경:** 모든 통신은 API Key로 식별되며, 특히 셀러 등록 및 민감 데이터 처리 시 64자리의 헥사데시멀(Hexadecimal) 보안 키를 활용한 JWE 암호화 방식을 강제하고, 웹훅 요청은 Webhook-Signature 검증을 거쳐 철저한 무결성을 확보한다16.

### 6.2. 포트원: 다자간 마켓플레이스 정산 및 세무 파이프라인 통합

토스페이먼츠가 결제 원천사로서의 직관적인 자금 이체에 집중한다면, 포트원(PortOne)은 수십 개의 PG 망을 하나로 묶어주는 메타-PG의 장점을 넘어 다자간 파트너 정산과 세무 자동화라는 고도화된 비즈니스 파이프라인을 제공한다40. B2B 커머스나 셀러 수가 방대한 마켓플레이스에서 그 효용성이 극대화된다.

* **복합 수익 배분 수식 엔진:** 단순한 고정 비율 정산뿐만 아니라 플랫폼의 다양한 과금 모델을 수용한다40. 사용자가 사용한 쿠폰 및 포인트에 대한 할인 분담금, 마케팅 채널 비용, 풀필먼트 부가 수수료 등을 주문 금액과 함께 조합할 수 있는 다중 수식 편집기(주문 금액 \* 정률 + 정액 등)를 지원하여 비즈니스 부서의 유연한 정책 설정을 시스템 코드 수정 없이 처리한다41.
* **정교한 스케줄링 및 과금 주체 추적:** PlatformSettlementCycle 객체를 통해 지체일(Lag Days), 휴일 고려 기준(Holiday Before/After, Calendar Day)을 바탕으로 정산 실행일을 자동 계산한다40. 더불어 정산 금액을 부담하는 주체를 나타내는 PlatformPayer 필드(파트너 혹은 플랫폼)를 명시하여 내부 원장 기록 시 정확한 회계 매핑을 지원한다43.
* **다양한 인터페이스 지원:** 정산 데이터 관리를 위해 REST API뿐만 아니라 GraphQL 기반의 조회 기능을 제공하여, 클라이언트가 복잡한 다중 관계 데이터(계약 조건, 파트너 정보, 정산 주기 등)를 한 번의 쿼리로 필요한 형태만큼만 추출할 수 있게 한다43.

### 6.3. PG 및 정산 연동 전략의 요약 비교

각 시스템의 강점을 명확히 비교하면 다음과 같다.

| **비교 및 선택 기준** | **토스페이먼츠 (Toss Payments)** | **포트원 (PortOne)** |
| --- | --- | --- |
| **핵심 가치 제안 (Value Proposition)** | 최고 수준의 API 개발자 경험, 견고한 지급대행 인프라 | 메타-PG 연동의 파편화 해소, 복잡한 파트너 정산 세무 자동화 |
| **오픈마켓 정산 모델 (Payouts)** | 시스템 내 자금을 예치 후 셀러 계좌로 직접 송금 지시 | 다중 수식에 기반한 정산 금액 계산 및 세금계산서 연계 처리 |
| **API 및 데이터 조회 패러다임** | 철저한 RESTful 중심, 리소스 기반 동형 응답, Cursor 페이징 | REST API 및 GraphQL 혼용, 계층적 데이터 일괄 조회 강점 |
| **수수료 및 정책 유연성** | 직관적이고 고정된 수수료 처리 및 명세서 발행 | 포인트, 마케팅 비용, 분담금 등 복합 수식(정률/정액) 편집기 지원 |
| **규제 리스크 대응 메커니즘** | KYC 상태(KYC\_REQUIRED) 모니터링, JWE 암호화 강제 | 부가세법 기반 전자세금계산서 발행 및 국세청 연동 내재화 |
| **전략적 채택 권장 대상** | 자금 직접 분배가 핵심인 스타트업, 강력한 샌드박스 테스트 선호 기업 | 수많은 영세 파트너를 관리하며 세무 행정 리소스에 병목을 겪는 플랫폼 |

플랫폼은 헥사고날 아키텍처의 유연성을 십분 발휘하여, 결제 창을 띄우고 고객으로부터 자금을 수취하는 인바운드 결제 어댑터로는 토스페이먼츠를 주력으로 사용하되, 정산 내역의 산출과 세무 증빙의 교부 어댑터로는 포트원의 시스템을 활용하는 하이브리드 아키텍처를 구성할 수도 있다.

## 7. 세무 행정의 병목 타파: 전자세금계산서 역발행(Reverse-issuance) 프로세스

다수의 파트너를 입점시키는 플랫폼 비즈니스가 마주하는 가장 크고 예상치 못한 장애물은 데이터베이스 트랜잭션이 아닌, 부가가치세법에 따른 '세무 증빙'이라는 아날로그적 행정 절차다. 전년도 공급가액 8천만 원 이상 개인사업자를 비롯한 모든 과세 사업자는 법적으로 전자세금계산서를 의무 발행해야 한다44.

### 7.1. 전통적 정산 프로세스의 한계

전통적인 거래 흐름에서 플랫폼이 파트너에게 정산 대금을 지급하면, 수익을 인식하는 공급자인 파트너 측에서 플랫폼(공급받는 자)으로 정발행 세금계산서를 작성하여 교부해야 한다. 그러나 수백, 수천 명의 영세 셀러들을 대상으로 매달 며칠까지 정확한 금액의 세금계산서를 발행해 달라고 독촉하고, 잘못 기재된 금액을 반려하며, 누락된 세금계산서로 인해 정산을 지연시키는 과정은 플랫폼의 재무팀과 운영팀의 리소스를 극도로 소진시킨다40. 플랫폼의 스케일 아웃이 기술이 아닌 행정 인력 부족으로 가로막히는 것이다.

### 7.2. 역발행(Reverse-issuance) 프로세스의 구원

이를 혁신적으로 해결하는 절차가 바로 부가가치세법 제32조에 근거한 '세금계산서 역발행(Reverse-issuance)'이다44. 역발행이란 자금을 지급해야 하는 플랫폼(공급받는 자)이 자체 시스템의 데이터베이스에 확정된 정확한 정산 금액을 바탕으로 세금계산서를 '대리 작성'하여 파트너(공급자)에게 전송하고, 파트너는 단순히 이를 검토한 후 클릭 한 번으로 '승인'하여 국세청에 정식 발행되도록 하는 구조를 말한다44.

일반적으로 국세청 홈택스 시스템은 이러한 역발행 워크플로우를 기본 지원하지 않으므로, 기업들은 팝빌(Popbill), 스마트빌(Smartbill), 메이크빌(Makebill) 등과 같은 전문 EDI 연계 서비스 업체를 도입하여 자체 ERP 시스템에 API 형태로 연동하는 고비용의 통합 개발을 진행해야 했다44. 이 경우에도 파트너들이 팝빌과 같은 외부 제휴사에 직접 회원가입을 해야 하는 번거로움이 발생한다44.

### 7.3. 포트원의 통합 역발행 파이프라인

포트원의 파트너 정산 API는 이러한 세무 행정 절차를 자사의 백오피스 인터페이스에 완전히 내재화했다40.

* **통합 워크플로우 지원:** 포트원 관리자 콘솔 내에서 정산금 자동 계산 -> 세금계산서 대량 역발행 작성(최대 10만 건 CSV 일괄 업로드 지원) -> 공급자의 승인 -> 최종 지급대행 실행으로 이어지는 과정이 하나의 끊김 없는(Seamless) 워크플로우로 연결된다44.
* **파트너의 UX 최소화:** 가장 혁신적인 지점은 파트너(공급자)의 진입 장벽을 낮춘 것이다. 파트너는 제휴사(팝빌 등)에 번거롭게 직접 가입할 필요가 없다45. 플랫폼이 관리자 콘솔에서 파트너의 '국세청 연동' 버튼을 활성화하면 백그라운드에서 자동 가입이 처리되며47, 역발행이 요청되면 파트너는 이메일의 랜딩페이지를 열고 최초 1회 공동인증서(1년 정보 저장)만 등록한 뒤 즉시 '발행 승인' 버튼을 눌러 행정을 마무리할 수 있다45.
* **상태 추적의 가시성:** 플랫폼 관리자는 특정 파트너의 세금계산서가 '역발행 요청됨', '승인 대기 중', '발행 완료', '승인 거부' 중 어느 단계에 있는지 API 및 대시보드를 통해 실시간으로 모니터링할 수 있어 극도의 투명성을 확보한다45. 결과적으로 이러한 역발행 파이프라인의 도입은 세금계산서 발행 및 승인 처리 속도를 기존 대비 75% 이상 단축시키며, 단순 반복 업무에 투입되던 인력을 비즈니스 성장에 집중할 수 있도록 해준다41.

## 8. 결론

"빠른 MVP의 출시"와 "복잡한 정산/결제 시스템 확장을 위한 기반 마련"이라는 상호 배타적으로 보이는 두 목표는 뛰어난 아키텍처 비전과 시장 생태계에 대한 깊은 이해를 통해서만 조화롭게 달성될 수 있다. 초기부터 모든 것을 완벽한 분산 인프라로 구축하려는 시도는 실패를 부르며, 반대로 기초적인 데이터 불변성 규칙을 무시한 해킹성 코드는 비즈니스가 도약해야 할 결정적 순간에 시스템을 붕괴시킨다.

본 보고서의 분석을 종합하여, 다음과 같은 단계별 기술 발전 전략을 제언한다.

**Phase 1: 기반 구축과 격리 (MVP 런칭 단계)** 시스템은 마이크로서비스의 복잡성을 덜어낸 모듈러 모놀리스(Modular Monolith) 아키텍처로 구현하여 단일 저장소 환경에서의 빠른 CI/CD 파이프라인을 확보해야 한다. 내부 도메인 간 결합을 느슨하게 유지하면서, 외부 세계와의 통신은 헥사고날 아키텍처(포트와 어댑터)의 인터페이스로 철저히 차단한다. 데이터베이스 설계는 단순히 상태를 덮어쓰는 것이 아니라, 멱등성과 무결성이 보장된 복식부기(Double-entry) 기반의 추가 전용(Append-only) 원장 엔진으로 설계하여 향후 닥쳐올 모든 회계 감사와 분쟁에 대비해야 한다.

**Phase 2: 규제 대응 및 오프로딩 (비즈니스 안착 단계)** 전금법 등 강화된 규제와 컴플라이언스를 충족하기 위해, 초기 플랫폼이 막대한 자본금을 들여 PG 라이선스를 직접 취득하는 전략은 배제해야 한다. 대신 토스페이먼츠나 포트원이 제공하는 서브 가맹점 모델 및 정산 지급대행(Payouts) API를 주도되는 어댑터에 강력히 결합한다. 이를 통해 복잡한 KYC 인증, 지연 이자 관리, 자금 분리 관리(Escrow)의 법률적 책임과 트랜잭션 부하를 외부의 검증된 인프라로 오프로딩(Offloading)하여 법적 리스크를 선제적으로 회피한다.

**Phase 3: 세무 자동화와 점진적 스케일아웃 (고속 성장 단계)** 성장하는 마켓플레이스 환경에서 폭증하는 B2B 거래 증빙 문제를 해결하기 위해, 포트원의 세금계산서 역발행 자동화 파이프라인 시스템을 통합 연동하여 운영 조직의 행정 병목을 타파한다. 트래픽의 병목이 본격화되는 시점에는, 단일 코드베이스로 유지되던 모듈러 모놀리스 시스템 중 결제 트래픽을 전담하는 도메인 모듈부터 스트랭글러 피그 패턴을 적용해 순차적으로 마이크로서비스로 분리하며, 메시지 브로커 기반의 비동기 이벤트 환경으로 자연스럽게 진화시켜 나간다.

올바른 물리적 아키텍처(모듈러 모놀리스), 방어적인 소프트웨어 디자인 패턴(헥사고날 아키텍처), 수학적으로 증명된 데이터 모델(이중 입력 원장), 그리고 외부 인프라스트럭처의 한계를 보완하는 탁월한 전략적 판단만이 불확실성이 지배하는 핀테크 플랫폼 생태계에서 기업을 안전한 성공으로 이끌어 줄 것이다.

#### Works cited

1. How fintech platforms are built: Design, architecture, and scale | Applifting Blog, <https://applifting.io/blog/how-fintech-platforms-are-built-design-architecture-and-scale>
2. How to Build a Bank Ledger in Golang with PostgreSQL using the Double-Entry Accounting Principle. - freeCodeCamp, <https://www.freecodecamp.org/news/build-a-bank-ledger-in-go-with-postgresql-using-the-double-entry-accounting-principle/>
3. Ledger: Stripe's system for tracking and validating money movement | Stripe Dot Dev Blog, <https://stripe.dev/blog/ledger-stripe-system-for-tracking-and-validating-money-movement>
4. Ledger balance: definition, architecture, and fintech use cases | Formance Blog, <https://www.formance.com/blog/financial-operations/ledger-balance-for-product-and-engineering>
5. [단독] 티메프 사태 재발?… 부실 전금업자 14곳, 미정산금만 2000억원 - Chosunbiz, <https://biz.chosun.com/stock/finance/2024/09/11/YDHIFQI2FZGHHD6WSBRHBFJKRQ/>
6. 정부 티메프 대책 "정산주기 40일 이내로, 판매대금 별도관리" - 중앙일보, <https://www.joongang.co.kr/article/25269052>
7. [FULL] 티메프 사태 이후 전자금융거래법 개정안 주요 내용 및 규제 동향 - YouTube, <https://www.youtube.com/watch?v=Intd9uHik30>
8. ｢위메프·티몬 사태 대응방안｣ 지원실적 및 향후 조치계획, <https://mofe.go.kr/com/cmm/fms/FileDown.do;jsessionid=FLahzVsad5z3Lg3sI7py-nbc.node50?atchFileId=ATCH_000000000028191&fileSn=4>
9. [보도자료] 티메프 사태 재발 방지를 위한 전자지급결제대행(PG)업 제도개선안 발표, <https://www.fsc.go.kr/no010101/83047>
10. 고객지원 - Mainpay 전자결제서비스, <https://www.mainpay.co.kr/cs/faqList.do?gubun=A>
11. 티몬 · 위메프 사태의 문제점과 정책적 시사점 - 한국금융연구원, <https://www.kif.re.kr/kif4/publication/viewer?mid=20&vid=0&cno=338649&fcd=2024008852GY&ft=0>
12. 전자금융거래법상 전자지급결제대행업(PG업) 관련 규제체계 정비, <https://ihcf.or.kr/uploaded/board/newsletter_apply/_9b612cc83c958aca9bd2b63fcf5b4baf0.pdf>
13. 금융 당국 “백화점·프랜차이즈 등 내부 정산 PG업 등록 면제”… 유통업계 우려 해소 - 조선비즈, <https://biz.chosun.com/stock/finance/2025/09/11/CI7EK2YDJBB3RNWB5SHC2DDAB4/>
14. I. 「전자금융거래법 일부개정 법률안」 (이하 “「전금법 개정안」”), 국회 본회의 통과 - 법무법인 태평양, <https://www.bkl.co.kr/law/insight/newsletter/6313>
15. [보도설명] 결제대금 정산에 관여하는 경우 전자지급결제대행업(PG)으로 등록하여야 합니다., [https://www.fsc.go.kr/no010102/82523?srchCtgry=&curPage=&srchKey=&srchText=&srchBeginDt=&srchEndDt=](https://www.fsc.go.kr/no010102/82523?srchCtgry&curPage&srchKey&srchText&srchBeginDt&srchEndDt)
16. 지급대행하기 - 토스페이먼츠 개발자센터, <https://docs.tosspayments.com/guides/v2/payouts>
17. Modular Monolith vs Microservices in NestJS - DEV Community, <https://dev.to/geampiere/modular-monolith-vs-microservices-in-nestjs-223g>
18. Modular Monolith vs Microservices: When to Consolidate Your Architecture, <https://blog.whoisjsonapi.com/modular-monolith-vs-microservices/>
19. Stop Overcomplicating DDD: Why Modular Monoliths Are the Smarter Choice - Medium, [https://medium.com/@curiousraj/stop-overcomplicating-ddd-why-modular-monoliths-are-the-smarter-choice-c887e3850fe8](https://medium.com/%40curiousraj/stop-overcomplicating-ddd-why-modular-monoliths-are-the-smarter-choice-c887e3850fe8)
20. Taming Payroll with a Modular Monolith - Check, <https://www.checkhq.com/resources/blog/taming-payroll-with-a-modular-monolith>
21. Hexagonal Architecture (Ports and Adapters) - DEV Community, <https://dev.to/godofgeeks/hexagonal-architecture-ports-and-adapters-3ljb>
22. Hexagonal architecture pattern - AWS Prescriptive Guidance, <https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/hexagonal-architecture.html>
23. A Color Coded Guide to Ports and Adapters - 8th Light, <https://8thlight.com/insights/a-color-coded-guide-to-ports-and-adapters>
24. Ports and Adapters (Hexagonal Architecture), Explained with Two Real Codebases - Saad Hasan, <https://saadh393.github.io/blog/adapter-port-architecture-two-cases>
25. Hexagonal Architecture: Easy Integration Using Ports and Adapters - Armakuni, <https://www.armakuni.com/insights/hexagonal-architecture>
26. Building an Append-Only Ledger in NoSQL | by Ahmed Waseem - Medium, <https://ahmed-waseem.medium.com/building-an-append-only-ledger-in-nosql-caebd3786193>
27. Designing Double-Entry Ledgers for High-Throughput Fintech Scales - Bytesfield, <https://www.bytesfield.com.ng/blog/designing-double-entry-fintech-ledgers>
28. Designing a Real-Time Ledger System with Double-Entry Logic - FinLego, <https://finlego.com/blog/designing-a-real-time-ledger-system-with-double-entry-logic>
29. Ledger Implementation in PostgreSQL - Paul Gross, <https://www.pgrs.net/2025/03/24/pgledger-ledger-implementation-in-postgresql/>
30. Basic double-entry bookkeeping system, for PostgreSQL. - GitHub Gist, <https://gist.github.com/NYKevin/9433376>
31. The Twisp Financial Ledger Database, <https://www.twisp.com/docs/infrastructure/ledger-database>
32. How would you model append-only ledger/register rows in SQL? - Reddit, <https://www.reddit.com/r/SQL/comments/1thzqj0/how_would_you_model_appendonly_ledgerregister/>
33. Keep the Credit Ledger Off-Chain. Checkpoint It On-Chain. - DEV Community, <https://dev.to/newtorob/keep-the-credit-ledger-off-chain-checkpoint-it-on-chain-4acf>
34. pgr0ss/pgledger: A double entry ledger implementation in PostgreSQL - GitHub, <https://github.com/pgr0ss/pgledger>
35. DoubleEntryLedger — double\_entry\_ledger v0.4.0 - Hexdocs, <https://hexdocs.pm/double_entry_ledger/>
36. 토스페이먼츠의 Open API 생태계 - Toss Tech, <https://toss.tech/article/payments-legacy-4>
37. 부가 API - 토스페이먼츠 개발자센터, <https://docs.tosspayments.com/reference/additional>
38. 토스 정산 API 소개 - 토스페이 연동가이드, <https://docs-pay.toss.im/reference/settlement>
39. 정산 API - 토스페이 연동가이드, <https://docs-pay.toss.im/reference/settlement/detail>
40. 관리자콘솔 | 파트너 정산 자동화 - PortOne 헬프센터, <https://help.portone.io/category/admin-console/platform-settlement>
41. 포트원: 통합 결제·정산 AI 재무 인프라, <https://www.portone.io/>
42. 파트너 정산 자동화 서비스 가이드 - 포트원 결제 연동 Doc, <https://developers.portone.io/platform/ko/readme>
43. 정산 상세내역 관련 API - 포트원 결제 연동 Doc, <https://developers.portone.io/api/rest-v2/platform.transfer?v=v2>
44. 정산금 지급시 세금계산서 역발행이 필요한 이유 - 포트원, <https://blog.portone.io/ps_tax-invoice-reverse-issue/>
45. 세금계산서 역발행이 꼭 필요한 이유 - 플랫폼 업종 실전 사례 살펴보기, <https://blog.portone.io/ps_tax-invoice-reverse-issue-case/>
46. 정발행・역발행 세금계산서 서비스 - 포트원, <https://www.portone.io/tax-invoice>
47. 우리회사(공급받는자)의 역발행 기본 절차가 궁금해요! - PortOne 헬프센터 - 포트원, <https://help.portone.io/content/taxinvoice_reverse_issuance_buyer_process>
48. 실사용자를 위한 세금계산서 역발행 사용 가이드 AtoZ - PortOne 헬프센터, <https://help.portone.io/content/taxinvoice_guide_atoz>