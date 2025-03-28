 DreamBigin - Web Application Requirements
A social media platform for artists to collaborate and showcase their work.

1. User Management
1.1 Registration & Login
Users should be able to register and log in using OAuth authentication (Google, Twitter, Facebook, etc.).
Users should have the option to register with email and password as an alternative.
Implement two-factor authentication (2FA) for enhanced security.
Implement role-based access control for different types of users (Artists, Businesses, Admins).
1.2 User Profile
Users should be able to create and manage their profile with:
Profile Picture
Bio / Short Description
List of Skills (e.g., Acting, Guitar, Directing)
Social Media Links (Instagram, YouTube, TikTok, LinkedIn, Twitter, etc.)
Portfolio Section (Showcase previous work with images/videos)
1.3 Collaboration Requests
Users should be able to create collaboration projects specifying:
Title
Project Description
Required Skills (e.g., Cinematographer, Scriptwriter, Vocalist)
Project Type (Short Film, Music Band, Art Collaboration, etc.)
Collaboration Location (Remote / Onsite)
Deadline (if applicable)
Compensation (if any)
Interested artists can apply to collaborate or directly message the project owner.
2. Business Enrollment & Advertisements
2.1 Business Accounts
Businesses (e.g., Camera Rentals, Film Institutes) should be able to:
Register as a Business Account.
List services (e.g., Equipment Rental, Online/Offline Courses).
Promote offers and discounts on rentals or training programs.
Receive inquiries from artists through direct messaging.
2.2 Business Promotions
Business accounts should have an option to boost their services (paid promotion).
Integration with Google Ads / Facebook Ads API for external promotions.
Businesses should be able to post job openings (e.g., “Seeking Assistant Director for an upcoming project”).
3. Content Sharing & Engagement
3.1 Content Creation
Users should be able to write articles and blogs (like Medium).
Users can post external links (e.g., YouTube, Instagram, SoundCloud).
Users can upload images & video snippets to showcase their work.
3.2 Engagement Features
Like, Comment, and Share features for posts.
Follow / Unfollow feature to subscribe to other users’ content.
Trending Content Section based on user engagement.
Hashtags & Categories for easy discoverability.
Users should be able to embed multimedia (videos, audio, GIFs).
4. Messaging & Notifications
4.1 Direct Messaging
Real-time chat for users to discuss collaborations.
Businesses can communicate with artists about services.
Group Chats for multi-person collaboration discussions.
4.2 Notifications
In-app notifications for new collaboration requests, messages, likes, comments, etc.
Email & Push Notifications (configurable in settings).
Weekly summary emails about trending posts and collaboration opportunities.
5. Discoverability & Search
5.1 Search & Filters
Search for Users, Projects, Businesses, and Content.
Filters by Skills, Location, Availability, Experience Level.
AI-powered recommendations based on user interests and engagement.
5.2 Featured Artists & Businesses
A curated list of top-rated artists based on collaborations and community engagement.
Business Spotlights showcasing top rental providers and training institutes.
6. Monetization & Payments
6.1 Premium Features
Subscription-based premium profiles for enhanced visibility.
Paid promoted collaboration requests to reach more artists.
6.2 Payment Gateway
Integration with Stripe / PayPal for in-app payments.
Artists can donate to other artists or fund a project.
Businesses can accept payments for courses & rentals.
7. Admin Panel
User & Content Moderation (Report & Ban system for abusive content).
Collaboration Request Monitoring (Prevent spam/fraudulent requests).
Analytics Dashboard (Track engagement, active users, trending skills).
8. Technology Stack (Suggested)
Frontend: React / Angular with TypeScript & SCSS.
Backend: .NET Core (C#) or Node.js (Express) with REST APIs.
Database: PostgreSQL / MySQL for structured data.
Authentication: OAuth, Firebase Auth, or Identity Server.
Messaging & Notifications: WebSockets for real-time chat, Firebase for push notifications.
File Storage: AWS S3 / Azure Blob Storage for multimedia.
AI Integration: AI-powered recommendations for matching artists & projects.
Additional Enhancements
✅ AI-based Profile Recommendations – Suggests potential collaborations based on skills.
✅ NFT Art Marketplace (Future Scope) – Artists can sell digital artwork as NFTs.
✅ Live Streaming Events – Artists and businesses can host live Q&A sessions.
✅ Mobile App (Future Scope) – Extend functionality to iOS/Android apps.