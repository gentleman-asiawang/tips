<template>
  <el-scrollbar>
    <div style="padding: 10px 30px 0 30px;">
      <!-- Section for TIPS Icon and Statistics -->
      <div class="content-container">
        <!-- Section for TIPS Icon -->
        <div class="tips-icon-container">
          <img :src="mainpicUrl" alt="TIPS Logo" class="tips-logo" />
        </div>

        <!-- Statistics Card -->
        <div class="statistics-card">
          <div class="stat-item stat-orders">
            <div class="custom-statistic">
              <div class="stat-number">28</div>
              <div class="stat-title">Orders</div>
            </div>
          </div>
          <div class="stat-item stat-species">
            <div class="custom-statistic">
              <div class="stat-number">824</div>
              <div class="stat-title">Species</div>
            </div>
          </div>
          <div class="stat-item stat-structures">
            <div class="custom-statistic">
              <div class="stat-number">13,290,681</div>
              <div class="stat-title">Protein Structures</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Text Section only -->
      <div class="text-container">
        <p>
          <b>
            <span class="colored-tq">T</span>he
            <span class="colored-iq">I</span>nsect
            <span class="colored-pq">P</span>rotein
            <span class="colored-sq">S</span>tructure (<span class="colored-t">T</span>
            <span class="colored-i">I</span>
            <span class="colored-p">P</span>
            <span class="colored-s">S</span>) database
          </b>
          is an online platform featuring 13.29 million protein structures from 824 insects across all 28 orders. TIPS
          includes 1.66 million structures (12.5%) from the AlphaFold database and 11.63 million newly predicted
          structures (87.5%) from our study. The web server provides tools for searching, visualizing, and downloading
          protein structures. In addition, each protein is accompanied by a description annotated using functional known
          databases, if available.
        </p>
        <p class="p2">
          Wu W., Cui C., Zhu Y., Chen J., Wang Y., Liu Z., Gao H., Ou G.-Z., Liu C., Tao M., Chen Y., Pan R., Zhang G.,
          Cai H., Yang J., Chen X., Zhou X., Wang S., & Shen X.-X. 2025. Exploring protein functions and remote homologs
          across the insect tree of life with structural genomics.
        </p>


      </div>
      <div class="text-container2">
        <p>
          Designed by <a href="https://shenxlab.com/" target="_blank" style="text-decoration: none;">The Shen Lab</a>,
          Update August 2025.
        </p>
      </div>



    </div>

  </el-scrollbar>

</template>

<script setup>
import mainpicUrl from "~/assets/index_tree_reduced_size.png"; // 确保图片在 `src/assets/`
</script>

<style scoped>
/* Adjust the flex layout to ensure even width for each stat item */
.statistics-card {
  display: flex;
  justify-content: space-between;
  max-width: 1000px;
  /* Match the maximum width of the TIPS logo */
  height: 100px;
  margin: 10px auto;
  /* Center the statistics card */
}

.stat-item {
  text-align: center;
  flex-grow: 1;
  /* Ensure equal width for each statistic item */
  flex-basis: 0;
  /* Force all items to take up the same width */
  padding: 20px;
}

.stat-orders {
  background-color: #5c9bd4;
}

.stat-species {
  background-color: #714f82;
}

.stat-structures {
  background-color: #b29f5a;
}

.custom-statistic {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-number {
  margin-top: 1px;
  font-size: 28px;
  font-weight: bold;
  color: white;
  /* Set the color of the number */
}

.stat-title {
  margin-top: 8px;
  font-size: 20px;
  color: white;
  /* Set the color of the title */
  letter-spacing: 1px;
}

/* Container to make both logo and statistics have the same max width */
.content-container {
  max-width: 1100px;
  margin: 0 auto;
  margin-top: 20px;
}

/* Max width for TIPS Logo */
.tips-logo {
  max-width: 100%;
  width: 1000px;
  height: auto;
  margin: 0 auto;
}

/* Text Section Styling */
.text-container {
  max-width: 1000px;
  margin: 0 auto;
  text-align: left;
  padding-top: 10px;
}


.text-container p {
  font-family: "Helvetica", Times, Sans-serif;
  font-size: 27px;
  line-height: 1.3;
  margin-top: 6px;
  text-align: justify;
}

.text-container .p2 {
  font-family: "Helvetica", Times, Sans-serif;
  font-size: 22px;
  line-height: 1.25;
  margin-top: 20px;
  text-align: justify;

}

.text-container2 {
  font-family: "Helvetica", Times, Sans-serif;
  font-size: 20px;
  line-height: 1.25;
  margin-top: 40px;
  text-align: center;
  font-weight: bold;
}

/* Colored text for TIPS */


.colored-tq {
  color: #156CC2;
  text-decoration: underline;
}

.colored-iq {
  color: #CC4227;
  text-decoration: underline;
}

.colored-pq {
  color: #1F8F39;
  text-decoration: underline;
}

.colored-sq {
  color: #E3C83B;
  text-decoration: underline;
}

.colored-t {
  color: #156CC2;
}

.colored-i {
  color: #CC4227;
}

.colored-p {
  color: #1F8F39;
}

.colored-s {
  color: #E3C83B;
}
</style>
