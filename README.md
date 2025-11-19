"# BizzAuto" 
1. Frontend with nextjs 16 and shadcn ui components library
2. backend with supabase and connect it with frontend using FastAPI
3. authentication with supabase and use mailtrap for verification
4. whatsapp api integration on message sending and scheduling messages
5. ocr for invoices, using redis and google vision api to extract text from images
6. inventory and alerts automatically sent via whatsapp. daily check worker for stock summary and expiry warnings.
7. Accounting (Basic ERP)
- Journal entries for invoices and payments. 
- Simple reports: sales summary, expense report and stock report.
8. Testing and deployment
- pytest for unit testing.
- Dockerized production deployment with managed Postgres, Redis and S3.
- Add Github Actions CI for init + test.
