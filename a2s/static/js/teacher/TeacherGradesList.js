document.addEventListener("DOMContentLoaded", async () => {
  const tbody = document.getElementById("studentTableBody");
  const uploadBtn = document.getElementById("uploadBtn");
  const fileUpload = document.getElementById("fileUpload");
  const downloadBtn = document.getElementById("downloadTemplateBtn");

  let students = [];

  // ===== Fetch students + grades =====
  async function fetchGrades() {
    try {
      const response = await fetch(`/teacher/api/teacher/class_grades/${COURSE_CODE}/${SECTION}/`);
      const data = await response.json();
      students = data.students || [];
      renderStudents(students);
    } catch (err) {
      console.error("Error fetching students:", err);
      tbody.innerHTML = "<tr><td colspan='7'>Failed to load students.</td></tr>";
    }
  }

  fetchGrades();

  // ===== Render table =====
  function renderStudents(list) {
    tbody.innerHTML = "";
    if (list.length > 0) {
      list.forEach(s => {
        const tr = document.createElement("tr");
        tr.dataset.studentId = s.student_id;
        tr.innerHTML = `
          <td>${s.id_number || "-"}</td>
          <td>${s.full_name || "-"}</td>
          <td class="midterm">${s.midterm || "-"}</td>
          <td class="final">${s.final || "-"}</td>
        `;
        tbody.appendChild(tr);
      });
    } else {
      tbody.innerHTML = "<tr><td colspan='7'>No students enrolled.</td></tr>";
    }
  }

  // ===== Download CSV Template =====
  downloadBtn.addEventListener("click", () => {
    if (!students || students.length === 0) return alert("No students loaded yet.");
    let csvContent = "id_number,midterm,final\n";
    students.forEach(s => {
      csvContent += `${s.id_number || ""},,\n`;
    });
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `${COURSE_CODE}_${SECTION}_grades_template.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  });

  // ===== Upload CSV/XLSX =====
  uploadBtn.addEventListener("click", () => {
    const file = fileUpload.files[0];
    if (!file) return alert("Please select a file to upload.");

    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: async (results) => {
        const uploadedGrades = results.data
          .map(g => ({
            id_number: (g["id_number"] || "").trim(),
            midterm: g["midterm"] || null,
            final: g["final"] || null
          }))
          .filter(g => g.id_number); // remove empty rows

        if (!uploadedGrades.length) return alert("No valid student rows found in file.");

        await saveGradesToBackend(uploadedGrades);
        await fetchGrades(); // refresh table
      },
      error: (err) => {
        console.error("Error parsing file:", err);
        alert("Failed to parse the file. Make sure it is CSV.");
      }
    });
  });

  // ===== Save grades to backend =====
  async function saveGradesToBackend(grades) {
    try {
      const response = await fetch(`/teacher/api/teacher/upload_grades/?course_code=${COURSE_CODE}&section=${SECTION}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify({ grades })
      });

      const result = await response.json();
      if (result.status === "success") {
        alert("Grades successfully uploaded!");
      } else {
        alert("Failed to upload grades: " + result.message);
      }
    } catch (err) {
      console.error("Error uploading grades:", err);
      alert("An error occurred while saving grades.");
    }
  }

  // ===== CSRF helper =====
  function getCSRFToken() {
    const name = "csrftoken";
    const cookies = document.cookie.split(";");
    for (let c of cookies) {
      const cookie = c.trim();
      if (cookie.startsWith(name + "=")) return cookie.substring(name.length + 1);
    }
    return "";
  }
});
