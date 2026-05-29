// MongoDB - no schema setup needed.
// Collection is created automatically on first insert.
// 
// Collection: wbs_jobs
// Sample document:
// {
//   "_id": "uuid-string",
//   "project_title": "My SSO",
//   "company_name": "ABC Pvt Ltd",
//   "project_manager": "Priyanka Pareek",
//   "team_size": 5,
//   "project_start_date": "01-Jun-26",
//   "rough_scope": "...",
//   "project_config": { "frontend": "Y", "backend": "Y", ... },
//   "recipient_email": "sales@company.com",
//   "status": "done",         // pending | running | done | failed
//   "error": null,
//   "created_at": ISODate,
//   "completed_at": ISODate
// }
//
// Just point MONGO_URI in .env to your MongoDB Atlas or company MongoDB.
// That's it.
