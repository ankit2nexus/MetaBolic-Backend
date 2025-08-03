import axios from "axios";

// Get API base URL based on environment
const getApiBaseUrl = () => {
  // Check if we're in production
  if (import.meta.env.PROD) {
    // Production API URL - replace with your actual Render backend URL
    return import.meta.env.VITE_BACKEND_API || "https://metabolical-backend.onrender.com/api/v1";
  } else {
    // Development API URL
    return import.meta.env.VITE_BACKEND_API || "http://localhost:8000/api/v1";
  }
};

const apiClient = axios.create({
  baseURL: getApiBaseUrl(),
  headers: {
    "Content-Type": "application/json",
  },
  params: {
    limit: 20,
  },
  timeout: 10000, // 10 second timeout
});

// Add request interceptor for debugging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

const dummyResponse = {
  status: 200,
  data: {
    articles: [
      {
        date: "2025-07-27T04:02:00",
        title:
          "The Silent Epidemic: Why Fatty Liver Is Becoming Increasingly Common In Young Adults - News18",
        authors: "News18",
        summary:
          "The Silent Epidemic: Why Fatty Liver Is Becoming Increasingly Common In Young Adults News18",
        url: "https://news.google.com/rss/articles/CBMi4gFBVV95cUxOOW00b3MwVkRjR000cmtGQ3FSeHlveHJqLTNGSDloWlVSR3J4RV8wT0J2NEFvZjJ1TWlOMFZicjJKczZ6TGhIclFacU11Ulp0dDJCWmw2S05ZallxczFDMHhwejJLTkxYYkk5ekhYWXhGb2JJSUw4aGs0ZGRIaFkwMEhUMGNkNE1Jd01CbVphOHVEZ2g5bVp1VTVoNFpDWGUwRURVT2Nab3lveDR3T2Nvd0Z2bnFEdElnQUNKNUJLWDJzVzUyVWRtTExNMmpOVk1xRlU3Rjc2ZmxMRGI4RjIyUEZ30gHnAUFVX3lxTE9PRlNiVEl6c21JbFdzXzVUWFAxaUJBUW1HVk1NS1pGMXVSbURIenI0b3JYaG9DUXBLSS1OYkcyNmJ3UlVHY0VSekVrdXdnWkl1TDVIdkM4QkRPY2ozMk5aalhrOVFjalpFb0hUZnJ6cnZ3TVU2eXFIX0M1WHlvTF9SNk1UZEVOOTNza3hmeDNJTjFiaTZRS2xwVDMxOTZCeWlxdmo4czdOMGc4MDMyb056S2Jkc29KcHhqQmcwemstVGotZFdtdFNZWFBJbUY5R3lXSWNfUTlaQ2RUS1kyTXBFZXhZeHFBUQ?oc=5",
        categories: ["news"],
        tags: ["recent_developments"],
      },
      {
        date: "2025-07-25T14:42:44",
        title:
          "The NIH RECOVER Program Announces Plan to Request Ancillary Studies",
        authors: "Unknown",
        summary:
          "Notice NOT-HL-25-027 from the NIH Guide for Grants and Contracts",
        url: "http://grants.nih.gov/grants/guide/notice-files/NOT-HL-25-027.html",
        categories: ["news"],
        tags: ["recent_developments"],
      },
      {
        date: "2025-07-25T14:41:22",
        title:
          "Request for Information: Inviting Feedback on the Proposed NIH Research Plan on Rehabilitation Scientific Themes FY26-FY30",
        authors: "Unknown",
        summary:
          "Notice NOT-HD-25-003 from the NIH Guide for Grants and Contracts",
        url: "http://grants.nih.gov/grants/guide/notice-files/NOT-HD-25-003.html",
        categories: ["news"],
        tags: ["medical_research"],
      },
      {
        date: "2025-07-24T17:23:08",
        title: "Findings of Research Misconduct - Liping Zhang",
        authors: "Unknown",
        summary:
          "Notice NOT-OD-25-097 from the NIH Guide for Grants and Contracts",
        url: "http://grants.nih.gov/grants/guide/notice-files/NOT-OD-25-097.html",
        categories: ["news"],
        tags: ["medical_research"],
      },
      {
        date: "2025-07-24T06:27:04",
        title: "NIH Intramural Research Program Access Planning Policy",
        authors: "Unknown",
        summary:
          "Notice NOT-OD-25-136 from the NIH Guide for Grants and Contracts",
        url: "http://grants.nih.gov/grants/guide/notice-files/NOT-OD-25-136.html",
        categories: ["news"],
        tags: ["medical_research"],
      },
      {
        date: "2025-07-22T05:16:30Z",
        title:
          "Teen bats are spawning new viruses—here’s why scientists are paying close attention",
        authors: "University of Sydney",
        summary:
          "New research from the University of Sydney sheds light on how coronaviruses emerge in bat populations, focusing on young bats as hotspots for infections and co-infections that may drive viral evolution. By analyzing thousands of samples over three years, scientists discovered that juvenile bats frequently host multiple coronaviruses simultaneously—offering a real-time window into how new strains might arise. These findings, while involving non-human-infecting viruses, provide a powerful model to forecast how dangerous variants could eventually spill over into humans, especially as environmental pressures bring bats closer to human habitats.",
        url: "https://www.sciencedaily.com/releases/2025/07/250722035556.htm",
        categories: ["news"],
        tags: ["latest"],
      },
      {
        date: "2025-07-21T21:50:43Z",
        title:
          "Magic mushrooms rewind aging in mice—could they do the same for humans?",
        authors: "Emory Health Sciences",
        summary:
          "A surprising discovery from Emory University shows that psilocin, the active metabolite of psychedelic mushrooms, can delay cellular aging and extend lifespan. Human cells lived over 50% longer, and mice treated with psilocybin not only lived 30% longer but also looked and aged better.",
        url: "https://www.sciencedaily.com/releases/2025/07/250721223838.htm",
        categories: ["news"],
        tags: ["latest"],
      },
      {
        date: "2025-07-21T18:30:00Z",
        title: "Artificial sweeteners and other sugar substitutes",
        authors: "Mayo Clinic Staff",
        summary:
          "Learn about the pros and cons of sugar substitutes, also called artificial sweeteners. Almost everyone likes a sugary snack. But if you often have foods and drinks with lots of added sugar, the empty calories can add up. Added sugar can play a part in weight gain. It also may raise your risk of serious health problems, such as diabetes and heart disease. You might try to stay away from table sugar by using less processed sweeteners such as honey and molasses. But these also are forms of added sugar. They add calories to your diet.",
        url: "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/artificial-sweeteners/art-20046936",
        categories: ["news"],
        tags: ["latest"],
      },
      {
        date: "2025-07-21T18:30:00Z",
        title: "Caffeine: How much is too much?",
        authors: "Mayo Clinic Staff",
        summary:
          "Caffeine has its perks, but it can pose problems too. Find out how much is too much and if you need to cut down. If you rely on caffeine to wake you up and keep you going, you aren't alone. Millions of people rely on caffeine every day to stay alert and improve concentration. Up to 400 milligrams (mg) of caffeine a day appears to be safe for most healthy adults. That's roughly the amount of caffeine in four cups of brewed coffee, 10 cans of cola or two \"energy shot\" drinks. Keep in mind that the actual caffeine content in beverages varies widely, especially among energy ...",
        url: "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/caffeine/art-20045678",
        categories: ["news"],
        tags: ["latest"],
      },
      {
        date: "2025-07-21T18:30:00Z",
        title: "Cuts of beef: A guide to the leanest selections",
        authors: "Mayo Clinic Staff",
        summary:
          "Find out which cuts of beef are lowest in fat and cholesterol. You might think red meat is off-limits if you're concerned about your health or trying to watch your weight. But in small amounts, leaner cuts of beef can be part of a healthy diet. Use this guide to make smart choices with plenty of flavor.",
        url: "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/cuts-of-beef/art-20043833",
        categories: ["news"],
        tags: ["latest"],
      },
      {
        date: "2025-07-21T18:30:00Z",
        title: "Water: How much should you drink every day?",
        authors: "Mayo Clinic Staff",
        summary:
          "Water is essential to good health. Are you getting enough? These guidelines can help you find out. How much water should you drink each day? It's a simple question with no easy answer. Studies have produced varying recommendations over the years. But your individual water needs depend on many factors, including your health, how active you are and where you live.",
        url: "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/water/art-20044256",
        categories: ["news"],
        tags: ["latest"],
      },
      {
        date: "2025-07-21T18:30:00Z",
        title: "Healthy meals start with planning",
        authors: "Mayo Clinic Staff",
        summary:
          "Your healthy meal plan is ready. Grocery shopping for nutritious food is done. But when you're ready to fill your plate, how much is too much? A plan for healthy eating includes knowing how much food your body needs. And then eating that amount, no more and no less. Two measurements can help you do this: serving size and portion size. A serving is the amount of a food or drink that people typically take in. You'll see the serving size on nutrition labels for packaged food. The label also tells you things like how many calories or grams of fat are in that serving of food.",
        url: "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/healthy-meals/art-20546806",
        categories: ["news"],
        tags: ["latest"],
      },
      {
        date: "2025-07-21T18:30:00Z",
        title: "Page Not Found",
        authors: "Mayo Clinic Staff",
        summary:
          "For access to Patient Online Services, click:Patient Online Services For access to Professional Online Services click:Professional Online Services Mayo Clinic Children’s Center: 855-MAYO-KID (855-629-6543, toll-free)",
        url: "https://www.mayoclinic.org/diseases-conditions/heart-disease/in-depth/heart-healthy-diet/art-200467020,https://www.mayoclinic.org/nutrition-and-pain/art-20208638",
        categories: ["news"],
        tags: ["latest"],
      },
      {
        date: "2025-07-21T18:30:00Z",
        title: "Portion control for weight loss",
        authors: "Mayo Clinic Staff",
        summary:
          "Trying to lose weight? Remember the size of the portions you eat. Research has shown that people almost always eat more food when offered larger portions. So portion control is important when you're trying to lose weight and keep it off. A portion is the amount of food you put on your plate. A serving is an exact amount of food. To better manage what you're eating, you could carry around measuring cups and spoons. Or instead, you could use everyday objects as reminders, also called cues, of correct serving sizes, as recommended by t...",
        url: "https://www.mayoclinic.org/healthy-lifestyle/weight-loss/in-depth/portion-control/art-20546800",
        categories: ["news"],
        tags: ["latest"],
      },
      {
        date: "2025-07-21T18:30:00Z",
        title: "Sodium: How to tame your salt habit",
        authors: "Mayo Clinic Staff",
        summary:
          "Find out how much sodium you need and learn how getting too much might affect your health. Are you getting more sodium than health experts suggest is wise? If so, it could lead to serious health problems. Sodium is a mineral. You can find it naturally in food, such as celery or milk. Manufacturers may also add sodium to processed food, such as bread. Sodium also is used to flavor food in condiments, such as soy sauce. When sodium is combined with another mineral called chloride, the two make table sa...",
        url: "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/sodium/art-20045479",
        categories: ["news"],
        tags: ["latest"],
      },
      {
        date: "2025-07-21T18:30:00Z",
        title: "Page not found.",
        authors: "NHS UK",
        summary:
          "If you entered a web address please check it was correct. Why not browse theNHS website homepageto find services and information?",
        url: "https://www.nhs.uk/conditions/type-1-diabetes/https://www.nhs.uk/conditions/type-2-diabetes/",
        categories: ["news"],
        tags: ["latest"],
      },
      {
        date: "2025-07-21T18:30:00Z",
        title: "Page not found.",
        authors: "NHS UK",
        summary:
          "If you entered a web address please check it was correct. Why not browse theNHS website homepageto find services and information?",
        url: "https://www.nhs.uk/conditions/type-1-diabetes/https://www.nhs.uk/conditions/type-2-diabetes/",
        categories: ["news"],
        tags: ["latest"],
      },
      {
        date: "2025-07-21T02:38:23Z",
        title:
          "A tiny chemistry hack just made mRNA vaccines safer, stronger, and smarter",
        authors:
          "University of Pennsylvania School of Engineering and Applied Science",
        summary:
          "What if mRNA vaccines could be made more powerful and less irritating? Scientists at the University of Pennsylvania have found a way to do just that—by tweaking a key molecule in the vaccine’s delivery system. Using a century-old chemical trick called the Mannich reaction, they added anti-inflammatory phenol groups to the lipids that carry mRNA into cells. The result? A new class of lipids that reduce side effects, boost gene-editing success, fight cancer more effectively, and supercharge vaccines like those for COVID-19. This breakthrough could change how we build the next generation of vaccines and therapies.",
        url: "https://www.sciencedaily.com/releases/2025/07/250720034024.htm",
        categories: ["news"],
        tags: ["latest"],
      },
      {
        date: "2025-07-20T18:30:00Z",
        title:
          "Effects of concurrent continuous aerobic and short rest resistance exercise training on metabolic biomarkers in type 2 diabetes patients: a systematic review and meta-analysis",
        authors: "Diabetology & Metabolic Syndrome",
        summary:
          "Continuous short-rest resistance training combined with continuous aerobic exercise is a time-efficient, safe and effective strategy for improving outcomes in patients with T2D [5, 6].\nThe forest plot further highlights an increasing trend in HDL levels, reinforcing the potential benefits of concurrent exercise training.\nThe forest plot further highlights a consistent trend in which TG decreased with concurrent training combining continuous aerobic exercise and short-rest resistance training.\nNotably, to the best of our knowledge, this meta-analysis is the first to specifically examine the metabolic effects of integrating continuous aerobic training with resistance training that employs brief inter-set rest periods.\nThis study demonstrated that combining short rest resistance and continuous aerobic training significantly improved HDL-C levels and reduced TC and TG levels.",
        url: "https://dmsjournal.biomedcentral.com/articles/10.1186/s13098-025-01838-x",
        categories: ["news", "diseases", "solutions"],
        tags: [
          "cardiovascular",
          "diabetes",
          "fitness",
          "metabolic",
          "international",
        ],
      },
      {
        date: "2025-07-20T18:30:00Z",
        title: "Dietary hormesis: beyond nutrition and energy supply",
        authors: "Nature",
        summary:
          "Among all hormetic contexts, dietary hormesis stands out as the safest and most convenient form of hormesis that can be seamlessly integrated into daily life.\nThis accessibility makes dietary hormesis an appealing strategy for enhancing resilience, preventing chronic diseases, and promoting overall well-being in everyday life.\nLife processes and health benefits influenced by dietary hormesis Dietary hormesis operates through multiple interconnected pathways, impacting metabolism, immune function, and the gut microbiota.\nDietary hormesis also involves metabolic reprogramming, where low doses of certain dietary compounds can shift metabolic pathways to favor health-promoting processes.\nThorough exploration of the public health implications is critical for translating dietary hormesis into actionable recommendations and dietary guidelines.",
        url: "https://www.nature.com/articles/s41538-025-00518-4",
        categories: ["news", "food", "trending", "diseases", "solutions"],
        tags: [
          "international",
          "natural_food",
          "gut_health",
          "metabolic",
          "prevention",
        ],
      },
    ],
    pagination: {
      page: 1,
      limit: 20,
      total: 259,
      total_pages: 13,
      has_next: true,
      has_prev: false,
    },
  },
};

export const getNewsByCategory = async (category = "news", pageParam = 1) => {
  try {
    const res = await apiClient.get(`/category/${category}?page=${pageParam}`);
    if (res.status !== 200) {
      throw new Error("Failed to fetch news by category");
    }
    return res.data;
  } catch (error) {
    console.log(error)
    throw error;
  }
};

export const getNewsByTag = async (tag, pageParam = 1) => {
  try {
    const res = await apiClient.get(`/tag/${tag}?page=${pageParam}`);
    if (res.status !== 200) {
      throw new Error("Failed to fetch news by category");
    }
    return res.data;
  } catch (error) {
    console.log(error)
    throw error;
  }
};

export const getNewsBySearch = async(searchTerm, pageParam = 1) => {
  try {
    const res = await apiClient.get(`/search`, {
      params: { q: searchTerm, page: pageParam },
    });
    
    if (res.status !== 200) {
      throw new Error("Failed to fetch news by category");
    }
    return res.data;
  } catch (error) {
    throw error;
  }
};
