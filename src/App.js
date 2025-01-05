import React, { useState, useEffect, useCallback } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import "./App.css";

const App = () => {
  const [papers, setPapers] = useState([]);
  const [filteredPapers, setFilteredPapers] = useState([]);
  const [filters, setFilters] = useState([]);
  const [categories, setCategories] = useState([]);
  const [sortOrder, setSortOrder] = useState("newest");

  useEffect(() => {
    fetch("/papers.json")
      .then((response) => response.json())
      .then((data) => {
        setPapers(data);
        setFilteredPapers(data);
        const allKeywords = [...new Set(data.flatMap((paper) => paper.keywords))];
        setCategories(allKeywords);
      });
  }, []);

  const applyFiltersAndSorting = useCallback(() => {
    let updatedPapers = [...papers];

    if (filters.length > 0) {
      updatedPapers = updatedPapers.filter((paper) =>
        filters.every((filter) => paper.keywords.includes(filter))
      );
    }

    updatedPapers.sort((a, b) => (sortOrder === "newest" ? b.year - a.year : a.year - b.year));
    setFilteredPapers(updatedPapers);
  }, [papers, filters, sortOrder]);

  useEffect(() => {
    applyFiltersAndSorting();
  }, [filters, sortOrder, applyFiltersAndSorting]);

  const handleFilterChange = (keyword) => {
    setFilters((prev) =>
      prev.includes(keyword) ? prev.filter((k) => k !== keyword) : [...prev, keyword]
    );
  };

  return (
    <div className="container-layout">
      {/* Header */}
      <header className="header">
        <h3>Refereed Publications (Prof. Yew-Soon Ong)</h3>
        <input
          type="text"
          placeholder="Search by title or abstract..."
          onChange={(e) => {
            const query = e.target.value.toLowerCase();
            const searchResults = papers.filter(
              (paper) =>
                paper.title.toLowerCase().includes(query) ||
                paper.abstract.toLowerCase().includes(query)
            );
            setFilteredPapers(searchResults);
          }}
        />
      </header>

      {/* Main Content */}
      <div className="main-content">
        {/* Filter Layout */}
        <aside className="filter-layout">
          <h5>Filter by Keywords</h5>
          {categories.map((keyword) => (
            <div className="form-check" key={keyword}>
              <input
                type="checkbox"
                className="form-check-input"
                checked={filters.includes(keyword)}
                onChange={() => handleFilterChange(keyword)}
              />
              <label className="form-check-label">{keyword}</label>
            </div>
          ))}
        </aside>

        {/* Paper Section */}
        <div className="paper-section">
          {/* Paper Header */}
          <div className="paper-header">
            <div>
              <strong>{filteredPapers.length}</strong> papers shown
            </div>
            <div>
              <label className="me-2">Sort by Year:</label>
              <select
                className="form-select d-inline-block w-auto"
                value={sortOrder}
                onChange={(e) => setSortOrder(e.target.value)}
              >
                <option value="newest">Newest First</option>
                <option value="oldest">Oldest First</option>
              </select>
            </div>
          </div>

          {/* Paper Layout */}
          <main className="paper-layout">
            <div className="row">
              {filteredPapers.map((paper) => (
                <PaperCard key={paper.title} paper={paper} />
              ))}
            </div>
          </main>
        </div>
      </div>
    </div>
  );
};

// const PaperCard = ({ paper }) => {
//   const [showFullAbstract, setShowFullAbstract] = useState(false);

//   const highlightedAuthor = `<strong>Author:</strong> ${paper.author.replace(
//     /(Yew[-\s]Soon Ong)/gi,
//     '<span style="color: blue;">$1</span>'
//   )}`;

//   return (
//     <div className="col-md-6 mb-4">
//       <div className="card h-100 shadow">
//         <div className="card-body">
//           <h5 className="card-title text-primary">{paper.title}</h5>
//           <h6 className="card-subtitle mb-2 text-muted">Year: {paper.year}</h6>
//           <p
//             className="card-text"
//             dangerouslySetInnerHTML={{ __html: highlightedAuthor }}
//           ></p>
//           <p className="card-text">
//             {showFullAbstract
//               ? paper.abstract
//               : `${paper.abstract.substring(0, 100)}...`}
//             <button
//               className="btn btn-link p-0 ms-1"
//               onClick={() => setShowFullAbstract(!showFullAbstract)}
//             >
//               {showFullAbstract ? "Hide" : "Detail"}
//             </button>
//           </p>
//           <div>
//             {paper.keywords.map((kw) => (
//               <span key={kw} className="badge bg-primary me-1">
//                 {kw}
//               </span>
//             ))}
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// };

const PaperCard = ({ paper }) => {
  const [showFullAbstract, setShowFullAbstract] = useState(false);

  // Highlight the author's name "Yew-Soon Ong" or "Yew Soon Ong"
  const highlightedAuthor = `<strong>Author:</strong> ${paper.author.replace(
    /(Yew[-\s]Soon Ong)/gi,
    '<span style="color: blue;">$1</span>'
  )}`;

  return (
    <div className="col-md-6 mb-4">
      <div className="card h-100 shadow">
        <div className="card-body">
          {/* Conditionally render title as hyperlink */}
          {paper.url ? (
            <h5 className="card-title">
              <a href={paper.url} target="_blank" rel="noopener noreferrer" className="text-primary text-decoration-none">
                {paper.title}
              </a>
            </h5>
          ) : (
            <h5 className="card-title text-primary">{paper.title}</h5>
          )}
          <h6 className="card-subtitle mb-2 text-muted">Year: {paper.year}</h6>
          <p
            className="card-text"
            dangerouslySetInnerHTML={{ __html: highlightedAuthor }}
          ></p>
          <p className="card-text">
            {showFullAbstract
              ? paper.abstract
              : `${paper.abstract.substring(0, 100)}...`}
            <button
              className="btn btn-link p-0 ms-1"
              onClick={() => setShowFullAbstract(!showFullAbstract)}
            >
              {showFullAbstract ? "Hide" : "Detail"}
            </button>
          </p>
          <div>
            {paper.keywords.map((kw) => (
              <span key={kw} className="badge bg-primary me-1">
                {kw}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};


export default App;
