# Advanced AI-Based Hostel Management System

Final-year BE CSE/ISE project based on the supplied specification.

## Implemented foundation
- Java 17 + Spring Boot 3.x + Maven
- Spring MVC, JPA/Hibernate, MySQL, Spring Security, Thymeleaf
- REST APIs + Swagger/OpenAPI
- Admin login and role-aware security foundation
- Hostel/Block/Floor/Room/Student entities
- Room allocation and explainable recommendation scoring
- Attendance, leave and complaint entities
- AI complaint analysis with transparent NLP/rule classification
- Optional configurable LLM provider for chatbot integration
- Dashboard UI
- Docker + MySQL compose setup

## Run locally
1. Install JDK 17+, Maven 3.9+, MySQL 8.
2. Create DB: `mysql -u root -p < schema.sql`
3. Set `DB_USERNAME` and `DB_PASSWORD` if different from defaults.
4. Run `mvn clean spring-boot:run`.
5. Open `http://localhost:8080/login`.
6. API docs: `http://localhost:8080/swagger-ui/index.html`.

## Build
`mvn clean package`

## Docker
`mvn clean package -DskipTests`
then `docker compose up --build`

## AI provider
The project never hard-codes an API key. Set `AI_API_KEY`, `AI_PROVIDER_ENABLED=true`, `AI_PROVIDER_URL`, and `AI_MODEL`. The provider endpoint should accept an OpenAI-compatible chat request. Keep hostel-specific answers grounded in application data before exposing them to students.

## Important
This ZIP is a working project foundation, not a claim that every item in the 1108-line specification has been fully implemented. Modules such as payments, visitors, mess, notices, notifications, reports, audit logs, advanced forecasting, diagrams and full Postman collections should be completed as subsequent modules.
