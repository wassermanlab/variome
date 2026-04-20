/*
  Audit View — renders legacy pghistory event tables.
  Loaded by audit_view.html as a Babel/JSX script.
*/
const useState = React.useState;

function AuditView({ initialdata }) {
  const [activeTab, setActiveTab] = useState(0);
  const tables = initialdata.tables;

  if (!tables || tables.length === 0) {
    return <p style={{ margin: "1em" }}>No audit tables found.</p>;
  }

  const activeTable = tables[activeTab];

  return (
    <div>
      <div style={{ display: "flex", gap: "0.5em", marginBottom: "1em", flexWrap: "wrap" }}>
        {tables.map((table, i) => (
          <button
            key={i}
            className={"btn waves-effect waves-light" + (i === activeTab ? "" : " btn-flat")}
            style={i !== activeTab ? { color: "#163647", border: "1px solid #163647" } : {}}
            onClick={(e) => { e.preventDefault(); setActiveTab(i); }}
          >
            {table.label}
            <span style={{ marginLeft: "0.4em", fontSize: "0.8em", opacity: 0.8 }}>
              ({table.count})
            </span>
          </button>
        ))}
      </div>

      <TableView table={activeTable} />
    </div>
  );
}


function TableView({ table }) {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const PAGE_SIZE = 50;

  if (table.missing) {
    return (
      <div style={{ padding: "1em", background: "#fff", boxShadow: "0 2px 4px rgba(0,0,0,0.1)" }}>
        <p>
          Table <code>{table.name}</code> was not found in the database. This is
          expected on fresh installations that never ran pghistory.
        </p>
      </div>
    );
  }

  if (table.columns.length === 0) {
    return <p>No data available.</p>;
  }

  // Filter rows based on search string
  const lowerSearch = search.toLowerCase();
  const filteredRows = lowerSearch
    ? table.rows.filter((row) =>
        row.some((cell) => String(cell ?? "").toLowerCase().includes(lowerSearch))
      )
    : table.rows;

  const totalPages = Math.ceil(filteredRows.length / PAGE_SIZE);
  const pageRows = filteredRows.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  function handleSearch(e) {
    setSearch(e.target.value);
    setPage(0);
  }

  return (
    <div>
      <div style={{ marginBottom: "0.8em", display: "flex", alignItems: "center", gap: "1em" }}>
        <input
          type="text"
          placeholder="Filter rows…"
          value={search}
          onChange={handleSearch}
          style={{ padding: "0.3em 0.6em", border: "1px solid #ccc", borderRadius: "3px", minWidth: "220px" }}
        />
        <span style={{ color: "#555", fontSize: "0.9em" }}>
          {filteredRows.length} row{filteredRows.length !== 1 ? "s" : ""}
          {search ? ` matching "${search}"` : ""}
        </span>
      </div>

      <div style={{ overflowX: "auto" }}>
        <table style={{ borderCollapse: "collapse", width: "100%", background: "#fff", boxShadow: "0 2px 4px rgba(0,0,0,0.1)" }}>
          <thead>
            <tr>
              {table.columns.map((col, i) => (
                <th
                  key={i}
                  style={{
                    padding: "0.6em 0.8em",
                    background: "#163647",
                    color: "#fff",
                    textAlign: "left",
                    whiteSpace: "nowrap",
                    fontWeight: "600",
                    fontSize: "0.85em",
                  }}
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {pageRows.length === 0 && (
              <tr>
                <td
                  colSpan={table.columns.length}
                  style={{ textAlign: "center", padding: "1em", color: "#777" }}
                >
                  No rows to display.
                </td>
              </tr>
            )}
            {pageRows.map((row, ri) => (
              <tr
                key={ri}
                style={{ background: ri % 2 === 0 ? "#f9f9f9" : "#fff" }}
              >
                {row.map((cell, ci) => (
                  <td
                    key={ci}
                    style={{
                      padding: "0.4em 0.8em",
                      border: "1px solid #e0e0e0",
                      fontSize: "0.85em",
                      maxWidth: "280px",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                    title={String(cell ?? "")}
                  >
                    {String(cell ?? "")}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div style={{ display: "flex", gap: "0.4em", marginTop: "0.8em", alignItems: "center" }}>
          <button
            className="btn btn-small waves-effect waves-light"
            disabled={page === 0}
            onClick={(e) => { e.preventDefault(); setPage((p) => Math.max(0, p - 1)); }}
          >
            ‹ Prev
          </button>
          <span style={{ fontSize: "0.9em" }}>
            Page {page + 1} / {totalPages}
          </span>
          <button
            className="btn btn-small waves-effect waves-light"
            disabled={page >= totalPages - 1}
            onClick={(e) => { e.preventDefault(); setPage((p) => Math.min(totalPages - 1, p + 1)); }}
          >
            Next ›
          </button>
        </div>
      )}
    </div>
  );
}
