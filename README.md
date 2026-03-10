# 🎲 ValueBet Oracle: Sports Betting AI & Arbitrage Microservice

## 🚀 Quick Start

### 本地開發（三層同時啟動）

1. **ML Engine (Python)**  
   `cd ml-python-engine && python3 -m venv venv && source venv/bin/activate`  
   `pip install -r requirements.txt`  
   （Mac 若 XGBoost 無法載入請先 `brew install libomp`）  
   訓練模型：`python train_model.py [路徑/歷史賽事.csv]`（可略過，使用既有 `models/`）  
   啟動：`uvicorn main:app --reload --port 8000`

2. **Gateway (Rust)**  
   `cd backend-rust-gateway && cargo run`  
   預設監聽 `http://localhost:3000`，環境變數：`ML_ENGINE_URL`、`ODDS_API_KEY`（選填）。

3. **Frontend (Angular)**  
   `cd frontend-angular && npm ci && npm start`  
   瀏覽 `http://localhost:4200`，儀表板每 60 秒向 Gateway 輪詢價值投注。

### Docker 一鍵部署

- 將外部賠率 API 金鑰設為環境變數（選填）：  
  `echo "ODDS_API_KEY=your_key" > .env`
- 執行：`docker-compose up --build -d`
- 前端：http://localhost（Nginx）  
- Gateway API：http://localhost:3000  
- ML Engine 僅在內網供 Gateway 呼叫，不對外暴露 Port。

---

## 📂 Repository Structure (系統資料夾結構)
\`\`\`text
ValueBet Oracle/
├── frontend-angular/      # Angular 企業級前端儀表板
│   ├── src/app/           # 組件、服務、RxJS 輪詢
│   ├── Dockerfile         # Node 編譯 + Nginx 靜態
│   └── angular.json
├── backend-rust-gateway/  # Rust API Gateway (Axum)
│   ├── src/
│   │   ├── main.rs        # 進入點、Router、CORS
│   │   ├── handlers.rs    # GET /api/value-bets
│   │   ├── models.rs      # 賠率與 Python 請求/回傳結構
│   │   ├── services.rs    # 賠率 API、AI 預測、Value Edge
│   │   └── utils.rs       # 美式/小數賠率、隱含機率
│   ├── Cargo.toml
│   └── Dockerfile         # 多階段建置
├── ml-python-engine/      # Python 賽事預測微服務
│   ├── data/              # 歷史賽事 CSV（含 sample_matches.csv）
│   ├── models/            # XGBoost + Scaler (joblib)
│   ├── data_pipeline.py   # 清理、特徵工程
│   ├── train_model.py     # 訓練、評估、儲存模型
│   ├── main.py            # FastAPI POST /api/v1/predict
│   ├── requirements.txt
│   └── Dockerfile         # python:3.10-slim + Uvicorn
├── docker-compose.yml     # frontend, gateway, ml-engine 編排
└── README.md
\`\`\`

## 📝 專案深度解析 / Comprehensive Project Overview

本專案「ValueBet Oracle」是一個專為現代體育數據分析與合法運動博弈設計的智能化微服務系統。其核心宗旨並非盲目地預測比賽勝負，而是透過嚴謹的數據科學與機器學習演算法，尋找莊家（Bookmakers）在開出賠率時的計算盲點。在龐大的體育賽事市場中，莊家的賠率雖然是由專業精算師與複雜模型制定，但往往會受到大眾心理預期、熱門球隊效應以及突發新聞（如球員臨時受傷）的影響而產生偏差。本系統正是利用這種市場效率低下的時刻，透過自行訓練的 AI 模型計算出「真實勝率」，並與各家合法博弈平台（如台灣運彩、Bet365、Pinnacle）的「隱含勝率」進行交叉比對。當系統發現我們的預測勝率顯著高於莊家賠率所反映的機率時，便會自動將其標記為一個具有正向期望值的「價值投注（Value Bet）」。這不僅是一個極具商業潛力的應用，更是展現資料科學如何將冷冰冰的歷史數據轉化為實質決策建議的最佳範例。

在系統的宏觀架構設計上，我們採用了當今科技業極度推崇的「多語言微服務架構 (Polyglot Microservices)」，完美結合了 Python、Rust 與 Angular 三大技術棧的各自優勢。前端採用 Google 開發的 Angular 框架，負責建構一個響應式且即時更新的專業數據儀表板，讓使用者能一目了然地追蹤各場賽事的潛在利潤與賠率走勢。後端則大膽地切分為兩個獨立的微服務：一個是由 Rust 驅動的高效能 API Gateway，專職處理高頻率的外部賠率 API 請求、前端路由轉發以及嚴格的資料格式驗證；另一個則是由 Python 與 FastAPI 構成的 AI 運算大腦，專注於執行繁重的特徵工程與機器學習推論。這種職責分離的設計不僅大幅提升了系統的整體效能與穩定性，更確保了在未來面對海量賽事與即時賠率變動時，系統依然能保持極低的延遲與高度的可擴展性，展現了頂級軟體工程師對系統架構的深刻理解。

對於任何一個機器學習專案而言，數據的品質決定了模型的天花板，而在體育預測領域更是如此。本專案的數據獲取策略涵蓋了廣泛且深度的歷史維度，主要聚焦於資料結構最為完整且具備高度統計顯著性的籃球（NBA）或足球（英超）賽事。我們將透過自動化爬蟲技術或合法的體育數據 API（如 API-NBA 或 Sportmonks），收集過去數個賽季的逐場比賽紀錄。這些原始數據包含了極其豐富的細節，例如球隊的得分效率、投籃命中率、籃板控制率、主客場優勢、甚至是每一節的得分波動。除了球隊層級的數據，我們還會深入挖掘球員個人的進階數據（Advanced Stats），例如球員效率值（PER）、真實命中率（TS%）以及在場/不在場時的球隊淨勝分差（On/Off Court Plus-Minus）。透過建立這樣一個龐大且關聯性強的關聯型資料庫，我們為後續的 AI 模型訓練奠定了最為堅實且難以被輕易複製的數據基礎。

在獲取原始數據之後，緊接而來的是整個專案中最耗時、但也最能展現資料科學家功力的階段：「特徵工程（Feature Engineering）」。在這裡，我們將大量使用 Python 的 Pandas 與 NumPy 函式庫，將雜亂無章的比賽日誌轉化為模型能夠理解的數學特徵。我們不會只依賴單場比賽的得分，而是會利用 Pandas 的視窗函數（Window Functions）計算球隊在過去 5 場、10 場與整個賽季的移動平均表現（Rolling Averages）。此外，我們還會引入更為複雜的衍生特徵，例如衡量球隊實力隨時間衰減與增長的 Elo Rating 系統、考量球隊連續出賽帶來的「疲勞指數（Fatigue Index）」、以及衡量兩支球隊交手時的「球風克制關係（Matchup Disadvantage）」。這些經過精心計算的進階特徵，能夠幫助機器學習模型捕捉到隱藏在表面數據之下的深層戰術邏輯與球隊真實狀態，大幅提升預測的精準度與穩定性。



在機器學習演算法的選擇上，為了對應不同種類的博弈玩法，我們將採取雙管齊下的策略。針對「不讓分（Moneyline）」的純勝負預測，我們將其視為一個標準的二元分類問題（Binary Classification），並使用邏輯迴歸（Logistic Regression）或隨機森林（Random Forest）來輸出兩支球隊各自的獲勝機率。而針對「讓分盤（Point Spread）」或「大小分（Over/Under）」，這本質上是一個預測具體分數差距的任務，因此我們將採用強大的梯度提升樹（Gradient Boosting Trees，如 XGBoost 或 LightGBM）進行迴歸分析（Regression）。這些先進的演算法不僅具備極高的預測準確度，還能透過特徵重要性（Feature Importance）分析，告訴我們究竟是「三分球命中率」還是「防守籃板」對比賽勝負起到了決定性的作用。這使得我們的模型不再是一個難以解釋的黑盒子，而是一個具備強大洞察力的數據分析引擎。

評估模型好壞的標準，在這個專案中將與傳統的機器學習專案有著本質上的不同。在一般的分類任務中，我們通常追求最高的「準確率（Accuracy）」；但在價值投注預測系統中，純粹的準確率往往是一個虛榮指標。因為如果我們總是預測強隊獲勝，準確率可能高達七成，但由於莊家給強隊的賠率極低，長期下來反而會造成資金虧損。因此，我們系統的核心評估指標將轉向「預期投資報酬率（Expected ROI）」與「獲利因子（Profit Factor）」。我們會在驗證集（Validation Set）上進行嚴格的歷史回測（Backtesting），模擬系統如果根據模型預測進行下注，經過一個完整的賽季後，資金曲線的增長情況。只有當模型在回測中展現出穩定且正向的長期獲利能力時，我們才會將其部署到生產環境中，這種以真實商業利益為導向的評估方式，正是量化金融與演算法交易領域的標準做法。

擔任系統 AI 運算大腦的 Python 微服務，將透過 FastAPI 框架建構成一個高效能的 RESTful API。FastAPI 以其原生支援非同步處理（Asynchronous IO）與基於 Pydantic 的自動資料驗證而聞名，是目前部署機器學習模型的首選框架。在這個微服務啟動時，它會將訓練好的 XGBoost 模型與特徵標準化轉換器（Scalers）載入記憶體中待命。當接收到來自 Rust 閘道的推論請求（例如包含當晚比賽的兩支隊伍名稱與近期數據矩陣）時，Python 服務能在數毫秒內完成複雜的矩陣運算，並回傳精確的勝率機率分佈與預測分差。透過將 AI 推論邏輯獨立於單一微服務中，我們不僅確保了運算資源的專屬性，更讓未來的模型更新與 A/B 測試（例如同時運行舊版模型與新版神經網絡進行效能比較）變得輕而易舉，完全不會影響到整體系統的可用性。

引入 Rust 語言來打造 API Gateway，是本專案在系統架構上最為大膽且前瞻的決策。在體育賽事進行期間，各家博弈平台的即時賠率（Live Odds）變動極為頻繁，系統必須能夠以極高的頻率不斷向多個外部 API 輪詢最新數據，同時還要服務來自眾多前端用戶的連線請求。面對這種典型的高併發與 I/O 密集型場景，Rust 憑藉其無垃圾回收機制（Zero-cost Abstractions）與極致的記憶體安全特性，成為了完美的解決方案。我們將採用目前 Rust 生態系中最受推崇的 Axum 網頁框架，結合 Tokio 這個強大的非同步運行時，打造一個能夠輕鬆處理數萬個並行連線的超級中樞。Rust 閘道將負責統籌全局：它會並發地抓取外部賠率，呼叫內網的 Python 服務獲取預測勝率，然後將兩者進行數學比對，瞬間篩選出極具價值的投注標的。這種對系統效能的極致追求，將讓您的開發實力在同儕中徹底脫穎而出。

在 Rust 微服務的實作細節中，資料結構的嚴謹定義與錯誤處理機制是確保系統穩若泰山的關鍵。我們將大量使用 Rust 強大的型別系統與 `serde` 序列化套件，為外部 API 的回應、Python 服務的推論結果以及前端的請求定義精確的 Structs。任何格式不符的髒數據或惡意請求，都會在反序列化階段就被編譯器等級的安全機制直接攔截，徹底杜絕了傳統弱型別語言常見的執行時期崩潰。此外，考慮到外部第三方 API（如體育數據源）往往存在連線不穩或限流（Rate Limiting）的問題，我們會在 Rust 中實作完善的重試機制（Retry Policies）、斷路器模式（Circuit Breaker）與快取策略（如使用 Redis 快取短時間內未變動的賠率）。這些企業級後端開發的防禦性編程技巧，將確保 ValueBet Oracle 即使在面對外部網路動盪時，依然能為前端用戶提供不間斷的高品質服務。

前端使用者介面的建構，我們選擇了具備嚴謹架構與強大生態系的 Angular 框架。有別於簡單的靜態網頁，我們需要為使用者打造一個能夠即時處理大量數據流與複雜互動的專業儀表板（Dashboard）。Angular 原生內建的 TypeScript 支援，讓我們能夠在前端精準對應 Rust 傳遞過來的複雜型別，確保前後端資料交互的絕對安全。在這個儀表板中，使用者將能看到即將開打的賽事列表，系統會利用顏色編碼（如綠色代表高價值、紅色代表需避開）直觀地突顯出模型強烈推薦的價值投注。除了列表，我們還會整合強大的圖表庫（如 Chart.js 或 ECharts），將球隊的歷史戰績走勢、AI 預測機率分佈以及各家莊家的賠率變化曲線進行視覺化呈現。這不僅提升了系統的專業感，更讓使用者能夠在下注前，透過直觀的圖表快速消化背後複雜的數據邏輯，做出最理性的決策。

在 Angular 前端的資料狀態管理上，我們將深度運用其核心依賴之一：RxJS（Reactive Extensions for JavaScript）。由於體育賽事的賠率與狀態是動態變化的，傳統的 Promise 請求模式已經無法滿足即時更新的需求。透過 RxJS 的可觀察對象（Observables）與強大的操作符（Operators），我們能夠輕鬆地建立輪詢機制（Polling）或是建立 WebSockets 連線，將後端 Rust 閘道推送過來的最新賠率變動，轉化為持續不斷的數據流。前端組件只需訂閱（Subscribe）這些數據流，就能在不刷新頁面的情況下，自動且平滑地更新畫面上的賠率數字與預期利潤。這種響應式編程（Reactive Programming）的思維，不僅大幅減少了前端代碼的耦合度，更創造出了如同專業股票交易軟體般流暢且零延遲的極致使用者體驗。

為了解決合法博弈中的風險控管問題，我們將在系統中內建一套基於凱利準則（Kelly Criterion）的資金管理模組。這個模組會結合使用者的總本金、AI 預測的勝率以及當前莊家提供的賠率，透過嚴密的數學公式，自動計算出針對每一場價值投注的「最佳下注金額比例」。這意味著系統不僅告訴你「該買哪一隊」，還會告訴你「該下多少錢」。透過這種科學化的資金配置策略，我們能有效避免使用者因為過度自信而在單一賽事中投入過多資金，確保在長期的投注過程中，即使面臨短期的連敗波動，資金池依然能夠保持穩定並持續增長。這個功能的加入，將整個系統的定位從一個單純的「預測工具」昇華為一個全方位的「量化投資顧問」。

在現代軟體工程中，開發完成只是第一步，如何穩定且高效地部署系統同樣重要。本專案將全面擁抱 Docker 容器化技術，為微服務架構提供最可靠的運行環境。我們將為 Python 推論大腦撰寫基於輕量級 Linux 映像檔的 Dockerfile，確保所有 NumPy 與 Scikit-learn 的 C 語言依賴都能被正確編譯。對於 Rust API Gateway，我們將運用 Docker 的多階段建置（Multi-stage Builds）技術，先在編譯容器中建置出極小體積的執行檔，再將其複製到極簡的運行環境中，這通常能將最終映像檔的大小壓縮至幾十 MB 內，大幅加快部署速度。而 Angular 前端則會被編譯為靜態檔案，並交由 Nginx 容器進行高效能的靜態資源託管。這三個各自獨立的容器，將透過 `docker-compose` 進行統一的網路編排與生命週期管理。

利用 `docker-compose.yml` 進行服務編排，我們能夠輕鬆在本地開發機或是雲端伺服器上，一鍵還原整個複雜的微服務生態。在設定檔中，我們會建立一個隔離的內部橋接網路（Internal Network），讓 Rust 閘道可以透過服務名稱（如 `http://python-ml-engine:8000`）安全且高速地與 Python 服務通訊，而 Python 服務的 Port 將完全對外封閉，只允許 Rust 進行存取。唯一對外開放的只有前端的 Nginx (Port 80/443) 以及 Rust 的公開 API 端點。這種「深度防禦」的網路安全架構，完美模擬了企業級系統的生產環境配置。此外，我們還能在設定中輕易地加入環境變數（Environment Variables）注入，方便我們在開發環境、測試環境與正式環境之間，靈活切換資料庫連線字串或是第三方 API 的存取金鑰。

展望這個專案的未來發展藍圖，ValueBet Oracle 擁有著令人興奮的無限可能。在完成初期的勝負與讓分預測後，我們規劃的下一步是進軍更具挑戰性的「場中投注（Live In-Play Betting）」。這將要求我們的模型能夠根據比賽進行中的即時數據（如某位關鍵球員犯規麻煩、或是某一節的連續得分高潮），在毫秒之間重新評估勝率，並搶在莊家調整賠率之前發出交易訊號。此外，我們還可以探索將深度學習領域的強化學習（Reinforcement Learning）引入系統中，讓 AI 代理人（Agent）在虛擬的博弈環境中不斷與歷史數據進行自我對弈，學習出超越傳統統計模型的最佳下注策略。這不僅是一個學術研究的絕佳題目，更具備著改變真實體育博弈市場生態的巨大潛力。