import type { LanguageCode } from "./constants";

export interface TranslationKeys {
  common: {
    yes: string;
    no: string;
    save: string;
    cancel: string;
    delete: string;
    edit: string;
    search: string;
    loading: string;
    error: string;
    success: string;
    back: string;
    next: string;
    submit: string;
    confirm: string;
    close: string;
    viewAll: string;
    viewMore: string;
    retry: string;
    retrying: string;
    noData: string;
    optional: string;
    required: string;
    all: string;
    none: string;
    enable: string;
    disable: string;
    searchPlaceholder: string;
    online: string;
    days: string;
    acres: string;
    hectares: string;
  };
  nav: {
    home: string;
    crops: string;
    disease: string;
    weather: string;
    market: string;
    finance: string;
    vendors: string;
    forum: string;
    support: string;
    admin: string;
    profile: string;
    settings: string;
    logout: string;
    knowledge: string;
    notifications: string;
  };
  auth: {
    login: string;
    register: string;
    loginTitle: string;
    registerTitle: string;
    phoneLabel: string;
    phonePlaceholder: string;
    sendOtp: string;
    otpLabel: string;
    otpPlaceholder: string;
    verifyLogin: string;
    loginSuccess: string;
    loginError: string;
    logoutSuccess: string;
    notRegistered: string;
    alreadyRegistered: string;
    registerNow: string;
    loginNow: string;
    nameLabel: string;
    namePlaceholder: string;
    emailLabel: string;
    emailPlaceholder: string;
    cityLabel: string;
    cityPlaceholder: string;
    stateLabel: string;
    statePlaceholder: string;
    languageLabel: string;
    registerSuccess: string;
    registerError: string;
    otpSent: string;
    otpResent: string;
    demoMode: string;
    googleLogin: string;
    subtitle: string;
    invalidPhone: string;
    enterOtp: string;
    resendIn: string;
    resending: string;
    resendOtp: string;
    nameRequired: string;
    cityRequired: string;
    stateRequired: string;
    joinTitle: string;
    createFreeAccount: string;
    selectYourState: string;
  };
  dashboard: {
    welcome: string;
    goodMorning: string;
    goodAfternoon: string;
    goodEvening: string;
    todayActions: string;
    activeCrops: string;
    totalLand: string;
    readyToHarvest: string;
    monthlyProfit: string;
    weatherSummary: string;
    marketSummary: string;
    loadingTasks: string;
    noTasksForToday: string;
    noCropsYet: string;
    weatherToday: string;
    weatherInArea: string;
    noMarketData: string;
  };
  crops: {
    title: string;
    addCrop: string;
    cropName: string;
    variety: string;
    sowingDate: string;
    expectedHarvest: string;
    area: string;
    areaUnit: string;
    status: string;
    active: string;
    harvested: string;
    failed: string;
    land: string;
    selectLand: string;
    selectCrop: string;
    noCrops: string;
    noCropsDesc: string;
    addFirstCrop: string;
    daysToHarvest: string;
    daysOld: string;
    calendar: string;
    cropDetails: string;
    searchPlaceholder: string;
    unableToLoad: string;
    unableToLoadDesc: string;
    noMatch: string;
    noMatchDesc: string;
    planted: string;
    growing: string;
    harvestReady: string;
    stepSelectCrop: string;
    stepDetails: string;
    stepReview: string;
    selectCropType: string;
    varietyOptional: string;
    varietyPlaceholder: string;
    sowingDateRequired: string;
    expectedHarvestDateOptional: string;
    areaRequired: string;
    acres: string;
    hectares: string;
    reviewConfirm: string;
    cropAdded: string;
    redirecting: string;
    addCropSuccess: string;
    addCropFailed: string;
    selectCropError: string;
    sowingDateError: string;
    areaError: string;
    daysSinceSowing: string;
    growth: string;
    sowing: string;
    harvest: string;
    logExpense: string;
    scanDisease: string;
    weatherShort: string;
    irrigationAction: string;
    upcomingTasks: string;
    expenseHistory: string;
    diseaseScanHistory: string;
    noExpensesYet: string;
    deleteConfirm: string;
    cropDeleted: string;
    cropDeleteFailed: string;
    editComingSoon: string;
    goBack: string;
    notFound: string;
    failedToLoad: string;
  };
  disease: {
    title: string;
    uploadImage: string;
    dragDrop: string;
    orCamera: string;
    analyze: string;
    analyzing: string;
    result: string;
    diseaseDetected: string;
    noDisease: string;
    confidence: string;
    severity: string;
    treatment: string;
    listenInLanguage: string;
    tryAnother: string;
    history: string;
    noHistory: string;
    noHistoryDesc: string;
    high: string;
    medium: string;
    low: string;
    uploadFirst: string;
    uploadFirstDesc: string;
    plantDoctor: string;
    scanDescription: string;
    scanNow: string;
    recentScans: string;
    scanFirstPlant: string;
    scanFirstPlantDesc: string;
    quickTips: string;
    tip1: string;
    tip2: string;
    tip3: string;
    healthy: string;
    diseased: string;
    scanPlant: string;
    takePhotoDesc: string;
    takePhoto: string;
    pointCamera: string;
    chooseFromGallery: string;
    photoTips: string;
    tipNaturalLight: string;
    tipGetClose: string;
    tipIncludeAreas: string;
    tipAvoidBlurry: string;
    analysisFailed: string;
    analysisTips: string;
    dismiss: string;
    retake: string;
    analyzePlant: string;
    analyzingPlant: string;
    analyzingDesc: string;
    analysisComplete: string;
    scanAnotherPlant: string;
    scanSaved: string;
    couldNotLoadScan: string;
    selectImageFirst: string;
    analysisFailedRetry: string;
    needsImmediateAttention: string;
    takeActionToday: string;
    healthyPlant: string;
    whatWeSee: string;
    treatmentOptions: string;
    organicTreatment: string;
    chemicalTreatment: string;
    prevention: string;
    saveToHistory: string;
    askMitra: string;
    captured: string;
    afterTreatment: string;
    confidenceLabel: string;
  };
  weather: {
    title: string;
    currentWeather: string;
    forecast: string;
    temperature: string;
    humidity: string;
    rainfall: string;
    windSpeed: string;
    feelsLike: string;
    farmingAdvice: string;
    irrigation: string;
    enterCity: string;
    today: string;
    tomorrow: string;
    days: string;
    sunny: string;
    cloudy: string;
    rainy: string;
    pressure: string;
    highRisk: string;
    mediumRisk: string;
    lowRisk: string;
    loadError: string;
  };
  market: {
    title: string;
    currentPrice: string;
    priceTrend: string;
    bestDayToSell: string;
    selectCrop: string;
    noData: string;
    noDataDesc: string;
    priceUp: string;
    priceDown: string;
    priceStable: string;
    todayPrice: string;
    weeklyAvg: string;
    monthlyAvg: string;
    priceAlerts: string;
    loadError: string;
    mandi: string;
    msp: string;
    range: string;
    thirtyDays: string;
    allCropPrices: string;
    disclaimer: string;
    bestDayInfo: string;
  };
  finance: {
    title: string;
    totalExpenses: string;
    totalIncome: string;
    profit: string;
    loss: string;
    addExpense: string;
    addIncome: string;
    expenses: string;
    income: string;
    category: string;
    amount: string;
    date: string;
    description: string;
    noExpenses: string;
    noExpensesDesc: string;
    noIncome: string;
    noIncomeDesc: string;
    monthlyOverview: string;
    recentTransactions: string;
    expenseBreakdown: string;
    noFinancialData: string;
    noTransactions: string;
    cropSale: string;
    addFirstExpense: string;
    selectCategory: string;
    descriptionPlaceholder: string;
  };
  vendor: {
    title: string;
    searchCity: string;
    allCities: string;
    noVendors: string;
    noVendorsDesc: string;
    rating: string;
    reviews: string;
    addReview: string;
    distance: string;
    contact: string;
    viewDetails: string;
    failedToLoad: string;
    connectionError: string;
  };
  forum: {
    title: string;
    writePost: string;
    postPlaceholder: string;
    postButton: string;
    like: string;
    comment: string;
    comments: string;
    noPosts: string;
    noPostsDesc: string;
    writeComment: string;
    newPost: string;
    postTitlePlaceholder: string;
    postContentPlaceholder: string;
    failedToLoad: string;
    justNow: string;
  };
  support: {
    title: string;
    requestCallback: string;
    name: string;
    phone: string;
    city: string;
    message: string;
    submitRequest: string;
    requestSuccess: string;
    faq: string;
    contactUs: string;
    selectTopic: string;
    describeIssuePlaceholder: string;
    topicRequired: string;
    descriptionRequired: string;
    submitFailed: string;
    expertWillCall: string;
    submitAnother: string;
    cropDiseaseHelp: string;
    weatherAdvisory: string;
    marketPricesHelp: string;
    loanFinance: string;
    appTechnicalIssue: string;
    otherTopic: string;
    preferredTime: string;
    noPreference: string;
    morning: string;
    afternoon: string;
    evening: string;
    myPastRequests: string;
    noRequests: string;
  };
  mitra: {
    title: string;
    askAnything: string;
    thinking: string;
    voiceInput: string;
    typeMessage: string;
    send: string;
    startConversation: string;
    noConversations: string;
    greeting: string;
    welcomeMessage: string;
    newChat: string;
    online: string;
    quickActions: string;
    askAboutCrops: string;
  };
  admin: {
    title: string;
    totalFarmers: string;
    totalVendors: string;
    activeCrops: string;
    callRequests: string;
    addFarmer: string;
    addVendor: string;
    farmerList: string;
    vendorList: string;
    accessError: string;
    accessDenied: string;
    nameAndPhoneRequired: string;
    farmerAdded: string;
    failedToAddFarmer: string;
    allFieldsRequired: string;
    vendorAdded: string;
    failedToAddVendor: string;
    deactivateFarmer: string;
    deactivateVendor: string;
    deactivated: string;
    failedToDeactivate: string;
    noFarmersYet: string;
    noVendorsYet: string;
    recentSupportCalls: string;
    farmerNamePlaceholder: string;
    vendorNamePlaceholder: string;
    selectType: string;
    fertilizerDealer: string;
    pesticideShop: string;
    seedShop: string;
    equipmentDealer: string;
    buyerMandi: string;
  };
  profile: {
    settings: string;
    voiceInput: string;
    voiceDescription: string;
    notificationsEnabled: string;
    notificationsDesc: string;
    theme: string;
    darkMode: string;
    lightMode: string;
    appVersion: string;
    saving: string;
    editProfile: string;
    imageTooLarge: string;
    nameRequired: string;
    profileUpdated: string;
    profileUpdateFailed: string;
    confirmLogout: string;
    phoneCannotBeChanged: string;
  };
  notifications: {
    title: string;
    unread: string;
    markAllRead: string;
    noNotifications: string;
    noNotificationsAll: string;
    noNotificationsType: string;
    enablePush: string;
    enablePushDesc: string;
    enableNotifications: string;
  };
  knowledge: {
    title: string;
    description: string;
    searchPlaceholder: string;
    browseTopics: string;
    noTopics: string;
    noTopicsDesc: string;
  };
  landing: {
    voiceFirst: string;
    voiceFirstDesc: string;
    multilingual: string;
    multilingualDesc: string;
    diseaseDetection: string;
    diseaseDetectionDesc: string;
    weatherAlerts: string;
    weatherAlertsDesc: string;
    marketPricesFeature: string;
    marketPricesDesc: string;
    subtitle: string;
    empowering: string;
    getStarted: string;
    registerNow: string;
    everythingYouNeed: string;
    startFarmingSmarter: string;
    joinThousands: string;
    joinFree: string;
    madeWithLove: string;
  };
  dailyActions: {
    noActionsToday: string;
    todaysActions: string;
    done: string;
    allDone: string;
    greatJob: string;
  };
}

type Translations = Record<LanguageCode, TranslationKeys>;

export const translations: Partial<Translations> = {
  en: {
    common: {
      yes: "Yes",
      no: "No",
      save: "Save",
      cancel: "Cancel",
      delete: "Delete",
      edit: "Edit",
      search: "Search",
      loading: "Loading...",
      error: "Error",
      success: "Success",
      back: "Back",
      next: "Next",
      submit: "Submit",
      confirm: "Confirm",
      close: "Close",
      viewAll: "View All",
      viewMore: "View More",
      retry: "Retry",
      retrying: "Retrying...",
      noData: "No data available",
      optional: "Optional",
      required: "Required",
      all: "All",
      none: "None",
      enable: "Enable",
      disable: "Disable",
      searchPlaceholder: "Search...",
      online: "Online",
      days: "days",
      acres: "acres",
      hectares: "hectares",
    },
    nav: {
      home: "Home",
      crops: "My Crops",
      disease: "Disease",
      weather: "Weather",
      market: "Market",
      finance: "Finance",
      vendors: "Vendors",
      forum: "Forum",
      support: "Support",
      admin: "Admin",
      profile: "Profile",
      settings: "Settings",
      logout: "Logout",
      knowledge: "Knowledge",
      notifications: "Notifications",
    },
    auth: {
      login: "Login",
      register: "Register",
      loginTitle: "Login to Mithrava",
      registerTitle: "Join Mithrava",
      phoneLabel: "Phone Number",
      phonePlaceholder: "Enter 10-digit phone number",
      sendOtp: "Send OTP",
      otpLabel: "Enter OTP",
      otpPlaceholder: "000000",
      verifyLogin: "Verify & Login",
      loginSuccess: "Welcome back!",
      loginError: "Login failed. Please try again.",
      logoutSuccess: "Logged out successfully",
      notRegistered: "Not registered yet?",
      alreadyRegistered: "Already registered?",
      registerNow: "Register now",
      loginNow: "Login now",
      nameLabel: "Full Name",
      namePlaceholder: "Enter your name",
      emailLabel: "Email",
      emailPlaceholder: "Enter email (optional)",
      cityLabel: "City / Town",
      cityPlaceholder: "Enter your city",
      stateLabel: "State",
      statePlaceholder: "Enter your state",
      languageLabel: "Preferred Language",
      registerSuccess: "Registration successful!",
      registerError: "Registration failed. Please try again.",
      otpSent: "OTP sent to your phone",
      otpResent: "OTP resent",
      demoMode: "Demo Mode",
      googleLogin: "Continue with Google",
      subtitle: "Your AI farming companion",
      invalidPhone: "Please enter a valid 10-digit phone number",
      enterOtp: "Enter the complete 6-digit OTP",
      resendIn: "Resend OTP in",
      resending: "Resending...",
      resendOtp: "Resend OTP",
      nameRequired: "Please enter your name",
      cityRequired: "Please enter your city",
      stateRequired: "Please select your state",
      joinTitle: "Join Mithrava",
      createFreeAccount: "Create your free account",
      selectYourState: "Select your state",
    },
    dashboard: {
      welcome: "Welcome",
      goodMorning: "Good Morning",
      goodAfternoon: "Good Afternoon",
      goodEvening: "Good Evening",
      todayActions: "Today's Actions",
      activeCrops: "Active Crops",
      totalLand: "Total Land",
      readyToHarvest: "Ready to Harvest",
      monthlyProfit: "Monthly Profit",
      weatherSummary: "Weather Summary",
      marketSummary: "Market Summary",
      loadingTasks: "Loading today's tasks...",
      noTasksForToday: "No tasks for today. Add crops to see your schedule.",
      noCropsYet: "No crops yet. Add your first crop to get started!",
      weatherToday: "Weather Today",
      weatherInArea: "in your area",
      noMarketData: "No market data available",
    },
    crops: {
      title: "My Crops",
      addCrop: "Add Crop",
      cropName: "Crop Name",
      variety: "Variety",
      sowingDate: "Sowing Date",
      expectedHarvest: "Expected Harvest",
      area: "Area",
      areaUnit: "acres",
      status: "Status",
      active: "Active",
      harvested: "Harvested",
      failed: "Failed",
      land: "Land",
      selectLand: "Select Land",
      selectCrop: "Select Crop",
      noCrops: "No crops yet",
      noCropsDesc: "Start by adding your first crop to track it throughout the season.",
      addFirstCrop: "Add Your First Crop",
      daysToHarvest: "days to harvest",
      daysOld: "days old",
      calendar: "Calendar",
      cropDetails: "Crop Details",
      searchPlaceholder: "Search crops...",
      unableToLoad: "Unable to Load Crops",
      unableToLoadDesc: "Something went wrong while loading your crops. Please try again.",
      noMatch: "No crops match your search",
      noMatchDesc: "Try a different search or filter.",
      planted: "Planted",
      growing: "Growing",
      harvestReady: "Harvest Ready",
      stepSelectCrop: "Select Crop",
      stepDetails: "Details",
      stepReview: "Review",
      selectCropType: "Select Crop Type",
      varietyOptional: "Variety (Optional)",
      varietyPlaceholder: "e.g., Roma, HD-2967, Sona Masuri",
      sowingDateRequired: "Sowing Date *",
      expectedHarvestDateOptional: "Expected Harvest Date (Optional)",
      areaRequired: "Area *",
      acres: "Acres",
      hectares: "Hectares",
      reviewConfirm: "Review & Confirm",
      cropAdded: "Crop Added!",
      redirecting: "Redirecting to your crops...",
      addCropSuccess: "Crop added successfully!",
      addCropFailed: "Failed to add crop. Please try again.",
      selectCropError: "Please select a crop type",
      sowingDateError: "Please select sowing date",
      areaError: "Please enter valid area",
      daysSinceSowing: "days since sowing",
      growth: "Growth",
      sowing: "Sowing",
      harvest: "Harvest",
      logExpense: "Log Expense",
      scanDisease: "Scan Disease",
      weatherShort: "Weather",
      irrigationAction: "Irrigation",
      upcomingTasks: "Upcoming Tasks",
      expenseHistory: "Expense History",
      diseaseScanHistory: "Disease Scan History",
      noExpensesYet: "No expenses recorded yet",
      deleteConfirm: "Delete this crop? This action cannot be undone.",
      cropDeleted: "Crop deleted successfully",
      cropDeleteFailed: "Failed to delete crop",
      editComingSoon: "Edit coming soon!",
      goBack: "Go Back",
      notFound: "Crop not found",
      failedToLoad: "Failed to load crop details",
    },
    disease: {
      title: "Disease Detection",
      uploadImage: "Upload Image",
      dragDrop: "Drag & drop an image here, or click to upload",
      orCamera: "Or take a photo",
      analyze: "Analyze Image",
      analyzing: "Analyzing...",
      result: "Analysis Result",
      diseaseDetected: "Disease Detected",
      noDisease: "No Disease Detected",
      confidence: "Confidence",
      severity: "Severity",
      treatment: "Recommended Treatment",
      listenInLanguage: "Listen in your language",
      tryAnother: "Try Another Image",
      history: "Scan History",
      noHistory: "No scans yet",
      noHistoryDesc: "Upload a plant image to detect diseases.",
      high: "High",
      medium: "Medium",
      low: "Low",
      uploadFirst: "Upload an image first",
      uploadFirstDesc: "Take a photo or upload an image of your plant to detect diseases.",
      plantDoctor: "Plant Doctor",
      scanDescription: "Take a photo of your plant and our AI will diagnose any issues",
      scanNow: "Scan Now",
      recentScans: "Recent Scans",
      scanFirstPlant: "Scan First Plant",
      scanFirstPlantDesc: "Scan your first plant to get started with disease detection.",
      quickTips: "Quick Tips",
      tip1: "Take photos in good daylight for best results",
      tip2: "Focus on the affected leaves or stem",
      tip3: "Our AI can detect 50+ common crop diseases",
      healthy: "Healthy",
      diseased: "Diseased",
      scanPlant: "Scan Plant",
      takePhotoDesc: "Take a clear photo of the affected area",
      takePhoto: "Take a Photo",
      pointCamera: "Point camera at affected leaves",
      chooseFromGallery: "Choose from Gallery",
      photoTips: "Photo Tips",
      tipNaturalLight: "Use natural daylight for best results",
      tipGetClose: "Get close to the affected leaf or stem",
      tipIncludeAreas: "Include both healthy and affected areas in the photo",
      tipAvoidBlurry: "Avoid blurry or dark photos",
      analysisFailed: "Analysis Failed",
      analysisTips: "Tips: Make sure the image is clear, well-lit, and shows the affected area clearly.",
      dismiss: "Dismiss",
      retake: "Retake",
      analyzePlant: "Analyze Plant",
      analyzingPlant: "Analyzing your plant...",
      analyzingDesc: "Our AI is looking at leaf patterns, colors, and textures to identify any issues.",
      analysisComplete: "Analysis complete!",
      scanAnotherPlant: "Scan Another Plant",
      scanSaved: "Scan saved to history!",
      couldNotLoadScan: "Could not load scan result",
      selectImageFirst: "Please select an image first",
      analysisFailedRetry: "Analysis failed. Please try again.",
      needsImmediateAttention: "This needs immediate attention!",
      takeActionToday: "Take action today to save your crop",
      healthyPlant: "Healthy Plant",
      whatWeSee: "What We See",
      treatmentOptions: "Treatment Options",
      organicTreatment: "Organic Treatment",
      chemicalTreatment: "Chemical Treatment",
      prevention: "Prevention",
      saveToHistory: "Save to History",
      askMitra: "Ask Mitra",
      captured: "Captured",
      afterTreatment: "After Treatment",
      confidenceLabel: "confidence",
    },
    weather: {
      title: "Weather",
      currentWeather: "Current Weather",
      forecast: "7-Day Forecast",
      temperature: "Temperature",
      humidity: "Humidity",
      rainfall: "Rainfall",
      windSpeed: "Wind Speed",
      feelsLike: "Feels Like",
      farmingAdvice: "Farming Advice",
      irrigation: "Irrigation Recommendation",
      enterCity: "Enter your city",
      today: "Today",
      tomorrow: "Tomorrow",
      days: "days",
      sunny: "Sunny",
      cloudy: "Cloudy",
      rainy: "Rainy",
      pressure: "Pressure",
      highRisk: "High Risk",
      mediumRisk: "Medium Risk",
      lowRisk: "Low Risk",
      loadError: "Failed to load weather data",
    },
    market: {
      title: "Market Prices",
      currentPrice: "Current Price",
      priceTrend: "Price Trend",
      bestDayToSell: "Best Day to Sell",
      selectCrop: "Select a crop",
      noData: "No price data",
      noDataDesc: "Select a crop to view market prices.",
      priceUp: "Price Up",
      priceDown: "Price Down",
      priceStable: "Price Stable",
      todayPrice: "Today's Price",
      weeklyAvg: "Weekly Average",
      monthlyAvg: "Monthly Average",
      priceAlerts: "Price Alerts",
      loadError: "Failed to load market data",
      mandi: "Mandi",
      msp: "MSP",
      range: "Range",
      thirtyDays: "30 Days",
      allCropPrices: "All Crop Prices",
      disclaimer: "Prices are indicative and may vary by location. Always confirm with your local mandi.",
      bestDayInfo: "Based on historical data, this is usually the best day to sell.",
    },
    finance: {
      title: "Finance",
      totalExpenses: "Total Expenses",
      totalIncome: "Total Income",
      profit: "Profit",
      loss: "Loss",
      addExpense: "Add Expense",
      addIncome: "Add Income",
      expenses: "Expenses",
      income: "Income",
      category: "Category",
      amount: "Amount",
      date: "Date",
      description: "Description",
      noExpenses: "No expenses yet",
      noExpensesDesc: "Track your farming expenses to manage your finances.",
      noIncome: "No income recorded",
      noIncomeDesc: "Record your sales and income.",
      monthlyOverview: "Monthly Overview",
      recentTransactions: "Recent Transactions",
      expenseBreakdown: "Expense Breakdown",
      noFinancialData: "No financial data yet. Add your first expense to get started.",
      noTransactions: "No transactions yet",
      cropSale: "Crop sale",
      addFirstExpense: "Add First Expense",
      selectCategory: "Select category",
      descriptionPlaceholder: "What was it for?",
    },
    vendor: {
      title: "Vendors",
      searchCity: "Search by city",
      allCities: "All Cities",
      noVendors: "No vendors found",
      noVendorsDesc: "Try searching a different city.",
      rating: "Rating",
      reviews: "Reviews",
      addReview: "Add Review",
      distance: "Distance",
      contact: "Contact",
      viewDetails: "View Details",
      failedToLoad: "Failed to load vendors",
      connectionError: "Please check your connection and try again.",
    },
    forum: {
      title: "Community Forum",
      writePost: "Write a post...",
      postPlaceholder: "Share your farming experience or ask a question...",
      postButton: "Post",
      like: "Like",
      comment: "Comment",
      comments: "Comments",
      noPosts: "No posts yet",
      noPostsDesc: "Be the first to share something!",
      writeComment: "Write a comment...",
      newPost: "New Post",
      postTitlePlaceholder: "Post title...",
      postContentPlaceholder: "Share your experience or ask a question...",
      failedToLoad: "Failed to load posts. Please try again.",
      justNow: "Just now",
    },
    support: {
      title: "Expert Support",
      requestCallback: "Request a Callback",
      name: "Your Name",
      phone: "Phone Number",
      city: "City",
      message: "Describe your issue",
      submitRequest: "Request Callback",
      requestSuccess: "Callback requested! An expert will call you soon.",
      faq: "Frequently Asked Questions",
      contactUs: "Contact Us",
      selectTopic: "Select a topic",
      describeIssuePlaceholder: "Describe your issue or question...",
      topicRequired: "Please select a topic",
      descriptionRequired: "Please describe your issue",
      submitFailed: "Failed to submit request. Please try again.",
      expertWillCall: "Our expert will call you within 24 hours.",
      submitAnother: "Submit Another Request",
      cropDiseaseHelp: "Crop Disease Help",
      weatherAdvisory: "Weather Advisory",
      marketPricesHelp: "Market Prices",
      loanFinance: "Loan & Finance",
      appTechnicalIssue: "App Technical Issue",
      otherTopic: "Other",
      preferredTime: "Preferred Time",
      noPreference: "No preference",
      morning: "Morning (9 AM - 12 PM)",
      afternoon: "Afternoon (12 PM - 4 PM)",
      evening: "Evening (4 PM - 7 PM)",
      myPastRequests: "My Past Requests",
      noRequests: "No support requests yet",
    },
    mitra: {
      title: "Mitra - AI Assistant",
      askAnything: "Ask me anything about farming...",
      thinking: "Thinking...",
      voiceInput: "Voice Input",
      typeMessage: "Type a message...",
      send: "Send",
      startConversation: "Start a conversation with Mitra",
      noConversations: "No conversations yet",
      greeting: "Hello! I am Mitra, your AI farming assistant.",
      welcomeMessage: "How can I help you today? You can ask about crops, weather, diseases, or market prices.",
      newChat: "New Chat",
      online: "Online",
      quickActions: "Quick actions",
      askAboutCrops: "Ask me anything about your crops, weather, or market prices!",
    },
    admin: {
      title: "Admin Dashboard",
      totalFarmers: "Total Farmers",
      totalVendors: "Total Vendors",
      activeCrops: "Active Crops",
      callRequests: "Call Requests",
      addFarmer: "Add Farmer",
      addVendor: "Add Vendor",
      farmerList: "Farmer List",
      vendorList: "Vendor List",
      accessError: "Access Error",
      accessDenied: "You do not have admin access. Contact the administrator for access.",
      nameAndPhoneRequired: "Name and phone are required",
      farmerAdded: "Farmer added successfully",
      failedToAddFarmer: "Failed to add farmer",
      allFieldsRequired: "All fields are required",
      vendorAdded: "Vendor added successfully",
      failedToAddVendor: "Failed to add vendor",
      deactivateFarmer: "Deactivate farmer",
      deactivateVendor: "Deactivate vendor",
      deactivated: "deactivated",
      failedToDeactivate: "Failed to deactivate",
      noFarmersYet: "No farmers registered yet",
      noVendorsYet: "No vendors registered yet",
      recentSupportCalls: "Recent Support Calls",
      farmerNamePlaceholder: "Farmer name",
      vendorNamePlaceholder: "Vendor name",
      selectType: "Select type",
      fertilizerDealer: "Fertilizer Dealer",
      pesticideShop: "Pesticide Shop",
      seedShop: "Seed Shop",
      equipmentDealer: "Equipment Dealer",
      buyerMandi: "Buyer / Mandi",
    },
    profile: {
      settings: "Settings",
      voiceInput: "Voice Input",
      voiceDescription: "Enable voice commands in Mitra",
      notificationsEnabled: "Notifications",
      notificationsDesc: "Receive push notifications for weather alerts and updates",
      theme: "Theme",
      darkMode: "Dark mode",
      lightMode: "Light mode",
      appVersion: "App Version",
      saving: "Saving...",
      editProfile: "Edit Profile",
      imageTooLarge: "Image must be less than 5MB",
      nameRequired: "Name is required",
      profileUpdated: "Profile updated successfully!",
      profileUpdateFailed: "Failed to update profile. Please try again.",
      confirmLogout: "Are you sure you want to log out?",
      phoneCannotBeChanged: "Phone number cannot be changed",
    },
    notifications: {
      title: "Notifications",
      unread: "unread",
      markAllRead: "Mark all read",
      noNotifications: "No notifications",
      noNotificationsAll: "Weather alerts, price updates, and farming tips will appear here.",
      noNotificationsType: "No {type} notifications at the moment.",
      enablePush: "Enable push notifications",
      enablePushDesc: "Get real-time weather alerts, price updates, and farming tips.",
      enableNotifications: "Enable Notifications",
    },
    knowledge: {
      title: "Knowledge Base",
      description: "Everything you need to know about farming, crop management, and government schemes.",
      searchPlaceholder: "Search articles, crop tips, schemes...",
      browseTopics: "Browse Topics",
      noTopics: "No topics available",
      noTopicsDesc: "Knowledge categories will appear here.",
    },
    landing: {
      voiceFirst: "Voice-First",
      voiceFirstDesc: "Ask questions in your language. Get instant answers.",
      multilingual: "Multilingual",
      multilingualDesc: "Available in English, Hindi, Telugu, Kannada, and Tamil.",
      diseaseDetection: "Disease Detection",
      diseaseDetectionDesc: "Take a photo of your crop and get instant AI-powered diagnosis.",
      weatherAlerts: "Weather Alerts",
      weatherAlertsDesc: "Get personalized weather forecasts and farming advice for your area.",
      marketPricesFeature: "Market Prices",
      marketPricesDesc: "Real-time market prices and the best day to sell your crops.",
      subtitle: "Your AI Farming Companion",
      empowering: "Empowering Indian farmers with AI-powered tools for smarter farming.",
      getStarted: "Get Started",
      registerNow: "Register Now",
      everythingYouNeed: "Everything You Need",
      startFarmingSmarter: "Start Farming Smarter",
      joinThousands: "Join thousands of farmers who are already using Mithrava.",
      joinFree: "Join Mithrava Free",
      madeWithLove: "Made with love for Indian Farmers.",
    },
    dailyActions: {
      noActionsToday: "No actions for today. Enjoy your day!",
      todaysActions: "Today's Actions",
      done: "done",
      allDone: "All done for today!",
      greatJob: "Great job keeping up with your farm.",
    },
  },
};
