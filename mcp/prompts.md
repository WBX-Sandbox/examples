# Tested prompts

Prompts we ran in claude.ai with the WBX Sandbox connector (November 2026). Each links to a use case with the same task in Python.

**Analyse data that doesn't fit in a chat** – [big-dataset](../use-cases/big-dataset/)

> Analyze the NYC yellow taxi trips for June 2026: https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2026-06.parquet Don't paste the data into this chat. Download it into a WBX sandbox and work there. I want the number of trips, the busiest hours, average fare and tip by payment type, and the top 10 pickup zones. At the end, tell me how big the data was and how much of it actually came back into our conversation.

**Build and share a dashboard from that data**

> Build a small web dashboard from the NYC yellow taxi trips for June 2026 (https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2026-06.parquet): trips by hour, average tip by payment type and the top 10 pickup zones. Keep the data out of this chat: download it into a WBX sandbox, compute there, run the dashboard in the sandbox and give me the link.

**Spreadsheet → dashboard** (attach a CSV) – [csv-dashboard](../use-cases/csv-dashboard/)

> Here's our sales export for this year. Which products are growing and which are declining? Use WBX Sandbox to analyze it in Python, then make a small dashboard with a few charts and give me a link I can share with the team.

**A live web app with a link** – [share-web-app](../use-cases/share-web-app/)

> Make a simple web page where my team can vote on where to go for lunch today: Pizza Place, Sushi Bar, Burger Joint or Thai Kitchen. Show live results, run it in a WBX sandbox and give me a link I can share.

## Tips

- Say **"in a WBX sandbox"** explicitly – assistants often have their own built-in code tool.
- For large data, give a **URL** rather than an attachment: the sandbox downloads it directly, while an attachment has to be copied through the chat.
- Shared links carry an access token and stop working when the sandbox ends (ask the assistant to extend it if needed).
