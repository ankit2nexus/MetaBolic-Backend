const mockNewsApiResponse = {
  articles: [
    // === NEWS ===
    {
      title: "Government Unveils New Policy for Startups",
      summary:
        "A new policy aims to boost innovation and simplify compliance for startups across the country.",
      tags: ["Policy", "Startups", "Innovation"],
      url: "https://example.com/news/startup-policy",
      category: "News",
    },
    {
      title: "Supreme Court Delivers Landmark Verdict on Data Privacy",
      summary:
        "The court emphasizes the need for strong digital privacy protections.",
      tags: ["Legal", "Privacy", "India"],
      url: "https://example.com/news/data-privacy-verdict",
      category: "News",
    },
    {
      title: "Monsoon Arrives Early in Southern India",
      summary:
        "This year's monsoon arrived earlier than expected, benefiting farmers in Kerala and Tamil Nadu.",
      tags: ["Weather", "India", "Monsoon"],
      url: "https://example.com/news/monsoon-arrival",
      category: "News",
    },
    {
      title: "New Education Policy Receives Mixed Reactions",
      summary:
        "The recently proposed changes in curriculum have stirred debate among educators.",
      tags: ["Education", "Policy", "India"],
      url: "https://example.com/news/education-policy",
      category: "News",
    },
    {
      title: "Cybersecurity Breach Hits Major Bank",
      summary:
        "Sensitive user data was compromised in a recent cyberattack on a leading bank.",
      tags: ["Cybersecurity", "Finance", "Hacking"],
      url: "https://example.com/news/bank-breach",
      category: "News",
    },
    {
      title: "India and Japan Sign Renewable Energy Pact",
      summary:
        "The countries will collaborate on green energy projects and climate initiatives.",
      tags: ["India", "Japan", "Energy"],
      url: "https://example.com/news/energy-pact",
      category: "News",
    },
    {
      title: "Parliament Session Begins With Heated Debates",
      summary:
        "Opposition parties raised concerns over recent economic reforms.",
      tags: ["Politics", "India", "Debate"],
      url: "https://example.com/news/parliament-session",
      category: "News",
    },
    {
      title: "Tech Giant Acquires AI Startup for $1.2 Billion",
      summary:
        "The acquisition aims to strengthen the company’s presence in generative AI.",
      tags: ["Technology", "AI", "Business"],
      url: "https://example.com/news/ai-acquisition",
      category: "News",
    },
    {
      title: "Massive Fire Breaks Out in Delhi Warehouse",
      summary:
        "Firefighters battled flames for hours; no casualties reported.",
      tags: ["Accident", "Delhi", "Fire"],
      url: "https://example.com/news/delhi-fire",
      category: "News",
    },
    {
      title: "Public Transport to Go Electric by 2030",
      summary:
        "The new transport policy aims to make public buses 100% electric.",
      tags: ["EV", "Policy", "Transport"],
      url: "https://example.com/news/ev-public-transport",
      category: "News",
    },

    // === DISEASES ===
    {
      title: "New Dengue Variant Detected in Southeast Asia",
      summary:
        "Health authorities warn of more severe symptoms due to the new strain.",
      tags: ["Dengue", "Health", "Asia"],
      url: "https://example.com/diseases/dengue-variant",
      category: "Diseases",
    },
    {
      title: "Rising Diabetes Cases Alarm Health Officials",
      summary:
        "An increasing number of young adults are being diagnosed with Type 2 diabetes.",
      tags: ["Diabetes", "Lifestyle", "Health"],
      url: "https://example.com/diseases/diabetes-rise",
      category: "Diseases",
    },
    {
      title: "WHO Declares End to COVID-19 Global Emergency",
      summary:
        "Though COVID-19 is still active, the emergency phase is now over.",
      tags: ["COVID-19", "WHO", "Health"],
      url: "https://example.com/diseases/covid-declared-over",
      category: "Diseases",
    },
    {
      title: "Zika Virus Re-emerges in South America",
      summary: "Officials are monitoring an increase in Zika cases.",
      tags: ["Zika", "Virus", "South America"],
      url: "https://example.com/diseases/zika-alert",
      category: "Diseases",
    },
    {
      title: "Malaria Vaccine Shows 80% Effectiveness in Trials",
      summary:
        "A breakthrough in the fight against malaria, especially in Africa.",
      tags: ["Malaria", "Vaccine", "Science"],
      url: "https://example.com/diseases/malaria-vaccine",
      category: "Diseases",
    },
    {
      title: "India Launches TB Eradication Drive",
      summary:
        "A new campaign targets early detection and free medication.",
      tags: ["TB", "India", "Health"],
      url: "https://example.com/diseases/tb-drive",
      category: "Diseases",
    },
    {
      title: "Hepatitis Cases Linked to Contaminated Water",
      summary:
        "Rural areas face increasing cases due to lack of clean water.",
      tags: ["Hepatitis", "Water", "Sanitation"],
      url: "https://example.com/diseases/hepatitis-water",
      category: "Diseases",
    },
    {
      title: "Bird Flu Found in Migratory Birds",
      summary:
        "A fresh wave of bird flu has been detected along the migration route.",
      tags: ["Bird Flu", "Environment", "Animals"],
      url: "https://example.com/diseases/bird-flu",
      category: "Diseases",
    },
    {
      title: "Polio Virus Traces Detected in Sewage",
      summary: "Health officials launch a city-wide vaccination campaign.",
      tags: ["Polio", "Children", "Vaccination"],
      url: "https://example.com/diseases/polio-detected",
      category: "Diseases",
    },
    {
      title: "Rare Fungal Infection Spreads Among ICU Patients",
      summary:
        "Doctors are on high alert for mucormycosis cases post COVID.",
      tags: ["Fungal Infection", "Mucormycosis", "Hospitals"],
      url: "https://example.com/diseases/fungal-spread",
      category: "Diseases",
    },

    // === SOLUTIONS ===
    {
      title: "Startup Develops Portable Water Purifier for Villages",
      summary:
        "The device can provide clean water to over 1,000 people a day.",
      tags: ["Water", "Innovation", "Rural"],
      url: "https://example.com/solutions/water-purifier",
      category: "Solutions",
    },
    {
      title: "App Helps Farmers Detect Crop Disease with AI",
      summary:
        "Farmers can now use their smartphones to identify crop issues in seconds.",
      tags: ["Agriculture", "AI", "Farmers"],
      url: "https://example.com/solutions/farmer-ai-app",
      category: "Solutions",
    },
    {
      title: "City Launches Free E-Waste Pickup Program",
      summary:
        "Residents can now schedule pickups to safely dispose electronics.",
      tags: ["Environment", "Waste", "Urban"],
      url: "https://example.com/solutions/ewaste-pickup",
      category: "Solutions",
    },
    {
      title: "NGO Brings Solar Power to Remote Schools",
      summary:
        "Off-grid schools are now using solar energy for lighting and devices.",
      tags: ["Solar", "NGO", "Education"],
      url: "https://example.com/solutions/solar-schools",
      category: "Solutions",
    },
    {
      title: "AI Chatbot Provides Mental Health Support",
      summary:
        "Available 24/7, this free tool helps users manage anxiety and stress.",
      tags: ["Mental Health", "AI", "Healthcare"],
      url: "https://example.com/solutions/mental-health-bot",
      category: "Solutions",
    },
    {
      title: "Low-Cost Prosthetics Change Lives of Amputees",
      summary:
        "A new 3D-printing technique has made prosthetics more affordable.",
      tags: ["Health", "3D Printing", "Prosthetics"],
      url: "https://example.com/solutions/low-cost-prosthetics",
      category: "Solutions",
    },
    {
      title: "Biodegradable Packaging Adopted by Retail Chains",
      summary:
        "Several brands switch to eco-friendly packaging to reduce plastic use.",
      tags: ["Environment", "Packaging", "Retail"],
      url: "https://example.com/solutions/biopackaging",
      category: "Solutions",
    },
    {
      title: "Open-Source Platform Simplifies Legal Aid Access",
      summary:
        "Citizens can now access free legal help through a government-supported portal.",
      tags: ["Legal", "GovTech", "Justice"],
      url: "https://example.com/solutions/legal-aid-platform",
      category: "Solutions",
    },
    {
      title: "Smart Irrigation System Reduces Water Waste by 60%",
      summary:
        "Sensors and timers help optimize water usage in agriculture.",
      tags: ["Agritech", "Water", "Farming"],
      url: "https://example.com/solutions/smart-irrigation",
      category: "Solutions",
    },
    {
      title: "Online Tutoring Brings Quality Education to Rural Girls",
      summary:
        "A new project helps connect rural students with certified teachers via live classes.",
      tags: ["Education", "Rural", "Girls"],
      url: "https://example.com/solutions/online-tutoring",
      category: "Solutions",
    },
    {
      title: "5 Productivity Hacks for Remote Workers",
      summary:
        "Working from home? Try these simple techniques to stay focused and efficient.",
      tags: ["Productivity", "Remote Work", "Lifestyle"],
      url: "https://example.com/blogs/productivity-hacks",
      category: "Blogs",
    },
    {
      title: "My Journey to Minimalism",
      summary:
        "A personal story about letting go of clutter and finding peace.",
      tags: ["Minimalism", "Lifestyle", "Wellness"],
      url: "https://example.com/blogs/minimalism-journey",
      category: "Blogs",
    },
    {
      title: "How I Built My First Web App in 30 Days",
      summary:
        "A beginner’s guide to turning an idea into a working product.",
      tags: ["Coding", "Web Development", "Projects"],
      url: "https://example.com/blogs/webapp-30days",
      category: "Blogs",
    },
    {
      title: "Lessons from a Failed Startup",
      summary: "What I learned after my startup didn't succeed.",
      tags: ["Entrepreneurship", "Failure", "Startups"],
      url: "https://example.com/blogs/failed-startup",
      category: "Blogs",
    },
    {
      title: "10 Places to Visit in India Before You Die",
      summary:
        "A travel bucket list featuring incredible locations across the country.",
      tags: ["Travel", "India", "Adventure"],
      url: "https://example.com/blogs/india-travel-list",
      category: "Blogs",
    },
    {
      title: "Freelancing vs Full-Time Job: Which Is Better?",
      summary: "Pros and cons of working independently vs corporate roles.",
      tags: ["Freelance", "Careers", "Jobs"],
      url: "https://example.com/blogs/freelance-vs-job",
      category: "Blogs",
    },
    {
      title: "Building a Sustainable Skincare Routine",
      summary:
        "Eco-friendly products and practices that work for your skin.",
      tags: ["Sustainability", "Skincare", "Health"],
      url: "https://example.com/blogs/sustainable-skincare",
      category: "Blogs",
    },
    {
      title: "Daily Journaling Changed My Life",
      summary:
        "A habit that helped me improve mindfulness and mental clarity.",
      tags: ["Mental Health", "Journaling", "Well-being"],
      url: "https://example.com/blogs/journaling-benefits",
      category: "Blogs",
    },
    {
      title: "Why Everyone Should Learn Basic Coding",
      summary:
        "Understanding code can benefit your career and thinking skills.",
      tags: ["Coding", "Learning", "Career"],
      url: "https://example.com/blogs/why-learn-coding",
      category: "Blogs",
    },
    {
      title: "My Favorite Books of the Year",
      summary:
        "A list of fiction and nonfiction reads that made an impact.",
      tags: ["Books", "Reading", "Reviews"],
      url: "https://example.com/blogs/best-books",
      category: "Blogs",
    },

    // === AUDIENCE ===
    {
      title: "Youth Demand More Focus on Climate in Budget",
      summary:
        "Young citizens call for stronger environmental policies from the government.",
      tags: ["Youth", "Climate", "Policy"],
      url: "https://example.com/audience/youth-climate-budget",
      category: "Audience",
    },
    {
      title: "Senior Citizens Call for Better Public Transport",
      summary:
        "Older adults express the need for accessible buses and metro systems.",
      tags: ["Seniors", "Transport", "Public Service"],
      url: "https://example.com/audience/senior-transport",
      category: "Audience",
    },
    {
      title: "Students Voice Concerns About Exam Stress",
      summary:
        "A survey shows 78% of students experience anxiety before exams.",
      tags: ["Education", "Mental Health", "Students"],
      url: "https://example.com/audience/exam-stress",
      category: "Audience",
    },
    {
      title: "Rural Farmers Speak Out on Crop Insurance Delays",
      summary: "Delayed claims leave many farmers struggling post-harvest.",
      tags: ["Farmers", "Insurance", "Agriculture"],
      url: "https://example.com/audience/farmer-insurance",
      category: "Audience",
    },
    {
      title: "Women Entrepreneurs Face Funding Challenges",
      summary:
        "Lack of capital remains a barrier despite strong business ideas.",
      tags: ["Women", "Entrepreneurship", "Funding"],
      url: "https://example.com/audience/women-funding",
      category: "Audience",
    },
    {
      title: "Gig Workers Demand Health Benefits",
      summary:
        "Delivery drivers and freelancers call for medical coverage.",
      tags: ["Gig Economy", "Health", "Workers"],
      url: "https://example.com/audience/gig-health",
      category: "Audience",
    },
    {
      title: "Trans Community Advocates for Inclusive Jobs",
      summary:
        "A city-wide campaign promotes employment without discrimination.",
      tags: ["LGBTQ+", "Inclusion", "Workplace"],
      url: "https://example.com/audience/trans-jobs",
      category: "Audience",
    },
    {
      title: "Students Push for Skill-Based Learning",
      summary: "College forums promote practical knowledge over theory.",
      tags: ["Skills", "Education", "Students"],
      url: "https://example.com/audience/skill-learning",
      category: "Audience",
    },
    {
      title: "Urban Youth Support Digital Clean-Up Drive",
      summary:
        "A campaign to delete unused apps and files for digital hygiene.",
      tags: ["Youth", "Technology", "Digital"],
      url: "https://example.com/audience/digital-cleanup",
      category: "Audience",
    },
    {
      title: "Parents Want Better Online Safety for Kids",
      summary:
        "Concerns over internet safety prompt calls for stricter regulation.",
      tags: ["Online Safety", "Children", "Parenting"],
      url: "https://example.com/audience/online-safety-kids",
      category: "Audience",
    },

    // === FOOD ===
    {
      title: "5 Superfoods That Boost Immunity",
      summary: "Add these natural boosters to your daily diet.",
      tags: ["Health", "Nutrition", "Immunity"],
      url: "https://example.com/food/superfoods-immunity",
      category: "Food",
    },
    {
      title: "Street Food Festival Kicks Off in Delhi",
      summary: "Taste the best regional dishes at this week's event.",
      tags: ["Food", "Festival", "Delhi"],
      url: "https://example.com/food/street-food-delhi",
      category: "Food",
    },
    {
      title: "Plant-Based Diets Gain Popularity in Urban Areas",
      summary:
        "More people are choosing vegan meals for health and environment.",
      tags: ["Vegan", "Health", "Lifestyle"],
      url: "https://example.com/food/plant-based-trend",
      category: "Food",
    },
    {
      title: "How to Make the Perfect Masala Chai",
      summary: "A simple guide to India’s favorite tea.",
      tags: ["Recipes", "Beverages", "India"],
      url: "https://example.com/food/masala-chai-recipe",
      category: "Food",
    },
    {
      title: "Top 10 Must-Try Dishes from South India",
      summary: "A flavorful journey through dosas, idlis, and more.",
      tags: ["Regional Food", "South India", "Cuisine"],
      url: "https://example.com/food/south-indian-dishes",
      category: "Food",
    },
    {
      title: "What’s Really in Your Instant Noodles?",
      summary: "Breaking down the ingredients and health impact.",
      tags: ["Processed Food", "Nutrition", "Instant Meals"],
      url: "https://example.com/food/instant-noodles",
      category: "Food",
    },
    {
      title: "How to Eat Healthy on a Budget",
      summary: "Affordable tips for maintaining a nutritious diet.",
      tags: ["Budget", "Healthy Eating", "Tips"],
      url: "https://example.com/food/healthy-budget",
      category: "Food",
    },
    {
      title: "The Science Behind Fermented Foods",
      summary: "Why foods like yogurt and kimchi are good for your gut.",
      tags: ["Probiotics", "Digestion", "Science"],
      url: "https://example.com/food/fermented-benefits",
      category: "Food",
    },
    {
      title: "Farm-to-Table Trend Growing in Urban Cafes",
      summary: "Fresh, local produce is redefining restaurant menus.",
      tags: ["Organic", "Sustainability", "Restaurants"],
      url: "https://example.com/food/farm-to-table",
      category: "Food",
    },
    {
      title: "New Tech Keeps Fruits Fresh for Weeks",
      summary:
        "Food tech startup introduces shelf-life extension solution.",
      tags: ["Innovation", "FoodTech", "Preservation"],
      url: "https://example.com/food/fresh-fruit-tech",
      category: "Food",
    },

    // === TRENDING ===
    {
      title: "AI-Generated Music Goes Viral on Social Media",
      summary: "Songs created by machines are now topping charts.",
      tags: ["AI", "Music", "Social Media"],
      url: "https://example.com/trending/ai-music-trend",
      category: "Trending",
    },
    {
      title: "Metaverse Concerts Attract Millions of Fans",
      summary: "Virtual shows are redefining the music industry.",
      tags: ["Metaverse", "Entertainment", "Tech"],
      url: "https://example.com/trending/metaverse-concerts",
      category: "Trending",
    },
    {
      title: "‘Quiet Quitting’ Sparks Work Culture Debate",
      summary: "Employees are pushing back against hustle culture.",
      tags: ["Work", "Culture", "Trend"],
      url: "https://example.com/trending/quiet-quitting",
      category: "Trending",
    },
    {
      title: "Instagram Threads App Crosses 100M Users",
      summary: "Meta's newest app sets record-breaking growth.",
      tags: ["Instagram", "Apps", "Social"],
      url: "https://example.com/trending/threads-growth",
      category: "Trending",
    },
    {
      title: "Short-Form Video Continues to Dominate",
      summary:
        "Platforms like Reels, Shorts, and TikTok lead online engagement.",
      tags: ["Video", "Social Media", "Trends"],
      url: "https://example.com/trending/short-videos",
      category: "Trending",
    },
    {
      title: "Eco-Friendly Fashion Picks Up Momentum",
      summary: "Sustainable clothing brands see spike in sales.",
      tags: ["Fashion", "Sustainability", "Eco"],
      url: "https://example.com/trending/eco-fashion",
      category: "Trending",
    },
    {
      title: "Celebrities Join AI-Generated Content Craze",
      summary: "Stars are licensing their voices and faces to AI creators.",
      tags: ["Celebrities", "AI", "Media"],
      url: "https://example.com/trending/ai-celeb-content",
      category: "Trending",
    },
    {
      title: "Electric Bicycles Take Over City Streets",
      summary: "Urban commuters are ditching scooters for e-bikes.",
      tags: ["Mobility", "EV", "Urban"],
      url: "https://example.com/trending/electric-bikes",
      category: "Trending",
    },
    {
      title: "Digital Detox Retreats Are the New Travel Fad",
      summary: "People are paying to unplug and escape tech overload.",
      tags: ["Travel", "Wellness", "Digital"],
      url: "https://example.com/trending/digital-detox",
      category: "Trending",
    },
    {
      title: "Young Voters Use Memes to Promote Politics",
      summary: "Humor becomes a tool for civic engagement online.",
      tags: ["Politics", "Youth", "Memes"],
      url: "https://example.com/trending/meme-politics",
      category: "Trending",
    },
  ],
};

export const CATEGORIES = [
  "News",
  "Diseases",
  "Solutions",
  "Blogs",
  "Audience",
  "Food",
  "Trending",
];

export const newsApi = (category) => {
  const data = mockNewsApiResponse.articles.filter(
    (article) => article.category.toLowerCase() === category.toLowerCase()
  );

  return new Promise((resolve, reject) => {
    if (data) setTimeout(() => resolve(data), 2000);
    else reject("No data found");
  });
};
