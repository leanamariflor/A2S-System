  document.addEventListener("DOMContentLoaded", async () => {
    const tbody = document.getElementById("studentTableBody");

    try {
      const response = await fetch(`/teacher/api/teacher/classlist/${COURSE_CODE}/${SECTION}/`);
      const data = await response.json();

      tbody.innerHTML = ""; 

      if (data.students && data.students.length > 0) {
        data.students.forEach(s => {
          const tr = document.createElement("tr");
          tr.innerHTML = `
            <td>${s.full_name}</td>
            <td>${s.course_code}</td>
            <td>${s.section}</td>
            <td>${s.year_level}</td>
            <td>${s.program}</td>
            <td>
           <a href="/teacher/student/${s.id}/status/" class="view-btn">View Status</a>
          </td>
          `;
          tbody.appendChild(tr);
        });
      } else {
        tbody.innerHTML = "<tr><td colspan='4'>No students enrolled.</td></tr>";
      }
    } catch (err) {
      console.error("Error fetching students:", err);
      tbody.innerHTML = "<tr><td colspan='4'>Failed to load students.</td></tr>";
    }
  });
