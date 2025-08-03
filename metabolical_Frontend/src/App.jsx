import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Header from "./components/layout/Header";
import HomePage from "./Pages/HomePage";
import CategoryPage from "./Pages/CategoryPage";
import TagPage from "./Pages/TagPage";
import NotFoundPage from "./Pages/NotFoundPage";
import SearchPage from "./Pages/SearchPage";

function App() {
  return (
    <>
      <Router>
        <div className=" bg-gray-50 dark:bg-gray-950 w-full min-h-screen overflow-x-hidden">
          <Header />
          <main className="container mt-20 lg:mt-40 mx-auto px-4 py-6">
            <div className="w-full h-full flex flex-col items-center justify-center">
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/category/:category" element={<CategoryPage />} />
                <Route path="/tag/:tag" element={<TagPage />} />
                <Route path="/search/:query" element={<SearchPage />} />
                <Route path="*" element={<NotFoundPage />} />
              </Routes>
            </div>
          </main>
        </div>
      </Router>
    </>
  );
}

export default App;
