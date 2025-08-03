import React, { useState } from "react";
import { Menu, Plus, X } from "lucide-react";
import { menuArray } from "../../utils/CategoryData";
import { Link } from "react-router-dom";
import SearchBar from "../UI/SearchBar";

function Header() {
  const [openCategory, setOpenCategory] = useState("");
  const [openMenu, setOpenMenu] = useState(false);

  const toggleCategory = (category) => {
    if (openCategory === category) {
      setOpenCategory("");
    } else {
      // setOpenCategory("");
      setOpenCategory(category);
    }
  };

  const openMobileMenu = () => {
    setOpenMenu(true);
  };

  return (
    <>
      <header className="fixed z-50 w-full bg-white dark:bg-gray-900 shadow-md">
        <div className="px-4 py-3 flex items-center justify-between">
          <div className="text-2xl font-bold text-gray-800 dark:text-gray-100 flex-1">
            Metabolical
          </div>
          <div className="hidden lg:flex">
            <SearchBar />
          </div>
          {/* mobile nav icon*/}
          <button
            onClick={openMobileMenu}
            className="bg-violet-500 dark:bg-violet-700 lg:hidden p-2 rounded-full text-white shadow-sm cursor-pointer"
          >
            <Menu />
          </button>
          {/* mobile menu navigation */}
          <nav
            className={`lg:hidden absolute z-50 flex flex-col top-0 h-screen right-0 text-gray-700 dark:text-gray-100 shadow-md min-w-[230px] bg-white dark:bg-gray-800 transition-transform ${
              openMenu ? "translate-0" : "translate-x-96"
            }`}
          >
            <div className="p-2 text-right">
              <button
                onClick={() => setOpenMenu(false)}
                className="cursor-pointer hover:text-violet-700 mr-3"
              >
                <X size={20} strokeWidth={2.5} />
              </button>
            </div>
            <div className="px-3">
              <SearchBar />
            </div>
            <ul className="flex flex-col gap-2 flex-1 p-4 w-full overflow-y-auto">
              {menuArray?.map((menu) => (
                <li key={menu.category} className="">
                  <div className="flex items-center gap-2 ">
                    <Link
                      to={`/category/${menu.category}`}
                      className={`flex-1 hover:bg-violet-100 dark:hover:bg-violet-700 rounded-md p-2 transition-all font-medium ${openCategory === menu.category ? "bg-violet-100 dark:bg-violet-700" : "bg-transparent"}`}
                    >
                      {menu.title}
                    </Link>
                    {menu.tags && menu.tags.length > 0 && (
                      <button
                        onClick={() => toggleCategory(menu.category)}
                        className={` hover:text-gray-700 dark:hover:text-violet-700 cursor-pointer transition-all ${
                          openCategory === menu.category ? "rotate-45" : ""
                        }`}
                      >
                        <Plus size={18} strokeWidth={2.5} />
                      </button>
                    )}
                  </div>
                  {menu.tags && menu.tags.length > 0 && (
                    <div
                      className={`mt-2 ml-4 animate-in slide-in-from-top-2 duration-200 ${
                        openCategory === menu.category ? "block" : "hidden"
                      }`}
                    >
                      <ul className="flex flex-col gap-1 w-full">
                        {menu.tags.map((tag, tagIndex) => (
                          <li key={tagIndex}>
                            <Link
                              to={`/tag/${tag}`}
                              className="block text-left p-2 text-sm hover:bg-violet-50 dark:hover:bg-violet-700 dark:hover:text-gray-100 hover:text-violet-800 rounded-md transition-all capitalize"
                            >
                              {tag}
                            </Link>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </li>
              ))}
            </ul>
          </nav>
        </div>
        <div className=" hidden lg:block">
          <div className="container mx-auto py-4">
            <ul className="flex relative bg-gray-100 text-gray-600 dark:text-gray-100 dark:bg-gray-800 items-center justify-between space-x-6 mx-4 px-4 rounded-full">
              {menuArray.map((menu) => (
                <li
                  key={menu.category}
                  className="inline-block py-4 text-lg font-medium group"
                >
                  <Link
                    to={`/category/${menu.category}`}
                    className={` hover:text-violet-800 dark:hover:text-violet-500 transition-all `}
                  >
                    {menu.title}
                  </Link>
                  {menu.tags && menu.tags.length > 0 && (
                    <div className="absolute shadow text-gray-600 dark:text-gray-100 hidden group-hover:grid grid-cols-4 place-content-center p-4 top-[100%] left-0 w-full max-h-[200px] bg-white dark:bg-gray-800 rounded-md">
                      {menu.tags.map((tag, tagIndex) => (
                        <Link
                          key={tagIndex}
                          to={`/tag/${tag}`}
                          className="text-base  hover:bg-violet-50 hover:text-violet-800 dark:hover:text-gray-100 dark:hover:bg-violet-700 rounded-md transition-all capitalize p-2"
                        >
                          {tag}
                        </Link>
                      ))}
                    </div>
                  )}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </header>
    </>
  );
}

export default Header;
