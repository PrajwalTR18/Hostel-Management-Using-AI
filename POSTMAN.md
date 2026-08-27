# Postman endpoint checklist

Base URL: http://localhost:8080

- GET /api/students
- POST /api/students
- GET /api/rooms
- GET /api/room-allocations/recommend/{studentId}
- POST /api/room-allocations/{studentId}/{roomId}
- POST /api/complaints
- GET /api/complaints
- POST /api/ai/complaint-analysis body: {"text":"Water is leaking continuously from the bathroom pipe."}
- POST /api/ai/chat body: {"question":"What are the hostel rules?"}
- GET /api/dashboard
