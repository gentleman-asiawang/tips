<template>
  <el-scrollbar>
    <div class="text-container">
      <p class="title1">
        <span class="colored-t">T</span><span class="colored-i">I</span><span class="colored-p">P</span><span
          class="colored-s">S</span> Developers:
      </p>
      <p class="developer-name">Xing-Xing Shen</p>
      <p class="developer-name">Jinghua Yang</p>
      <p class="developer-name">Yazhou Wang</p>
      <p class="developer-name">Weiyin Wu</p>
      <p class="developer-name">Jingxuan Chen</p>
      <p class="contact-info"><strong>Contact:</strong> please contact Dr. Xing-Xing Shen
        (xingxingshen{at}zju.edu.cn)
        if you have any issues or requests about TIPS.</p>
    </div>

    <div class="citation-container">
      <p class="title2">How to Cite:</p>
      <p class="primary-citation">
        Wu W., Cui C., Zhu Y., Chen J., Zhuang Q., Wang Y., Liu Z., Gao H., Ou G.-Z., Liu C., Tao M., Chen Y., Pan R.,
        Zhang G.,
        Cai H., Yang J., Chen X., Zhou X., Wang S., & Shen X.-X. 2025. Structural genomics sheds light on
        protein functions and remote homologs across the insect tree of life.
      </p>
      <p class="info-text">Please also cite the relevant paper if you use the corresponding option:</p>

      <p class="info-text"><b>Sequence-based search by MMseqs2 v15.6f452:</b> Steinegger M., & Söding J. 2017.
        MMseqs2
        enables sensitive protein sequence searching for the analysis of massive data sets. <em>Nat
          Biotechnol</em>
        35, 1026–1028. https://doi.org/10.1038/nbt.3988.</p>
      <p class="info-text"><b>Structure-based search by Foldseek v9.427df8a:</b> van Kempen M., Kim S. S.,
        Tumescheit
        C., Mirdita M., Lee J., Gilchrist C. L. M., Söding J., & Steinegger M. 2024. Fast and accurate
        protein
        structure search with Foldseek. <em>Nat Biotechnol</em> 42, 243–246.
        https://doi.org/10.1038/s41587-023-01773-0.</p>
      <p class="info-text">Additionally, cite the AlphaFold paper if you use the protein structure predicted
        by
        AlphaFold2.</p>
      <p class="info-text"><b>AlphaFold:</b> Jumper J., Evans R., Pritzel A., Green T., Figurnov M.,
        Ronneberger O.,
        Tunyasuvunakool K., Bates R., Žídek A., Potapenko A., Bridgland A., Meyer C., Kohl S. A. A., Ballard
        A. J.,
        Cowie A., Romera-Paredes B., Nikolov S., Jain R., Adler J., Back T., Petersen S., Reiman D., Clancy
        E.,
        Zielinski M., Steinegger M., Pacholska M., Berghammer T., Bodenstein S., Silver D., Vinyals O.,
        Senior A. W.,
        Kavukcuoglu K., Kohli P., & Hassabis D. 2021. Highly accurate protein structure prediction with
        AlphaFold.
        <em>Nature</em> 596(7873), 583–589. https://doi.org/10.1038/s41586-021-03819-2.
      </p>
      <p class="info-text"><b>AlphaFold Protein Structure Database:</b> Varadi M., Bertoni D., Magana P.,
        Paramval U.,
        Pidruchna I., Radhakrishnan M., Tsenkov M., Nair S., Mirdita M., Yeo J., Kovalevskiy O.,
        Tunyasuvunakool K.,
        Laydon A., Žídek A., Tomlinson H., Hariharan D., Abrahamson J., Green T., Jumper J., Birney E.,
        Steinegger M.,
        Hassabis D., & Velankar S. 2024. AlphaFold Protein Structure Database in 2024: Providing structure
        coverage
        for over 214 million protein sequences. <em>Nucleic Acids Research</em> 52(D1), D368–D375.
        https://doi.org/10.1093/nar/gkad1011.</p>

    </div>
  </el-scrollbar>
</template>

<style scoped>
.text-container {
  max-width: 900px;
  text-align: left;
  line-height: 1.2;
  padding-top: 0px;
  margin: 0 auto;
}

.title1 {
  font-size: 28px;
  font-family: "Helvetica", Times, Sans-serif;
  margin-top: 10px;
  margin-bottom: 15px;
  font-weight: bold;
  line-height: 1.4;
  color: #333;
}

.title2 {
  font-size: 28px;
  font-family: "Helvetica", Times, Sans-serif;
  margin-top: 10px;
  margin-bottom: 10px;
  font-weight: bold;
  line-height: 1.25;
  color: #333;
}

.developer-name {
  font-size: 20px;
  line-height: 1;
  font-family: "Helvetica", Times, Sans-serif;
  margin-left: 0px;
  margin-top: 15px;
  margin-bottom: 5px;
}

.contact-info {
  margin-top: 10px;
  font-size: 22px;
  margin-left: 0px;
  text-align: justify;
  font-family: "Helvetica", Times, Sans-serif;
}


.citation-container {
  max-width: 900px;
  text-align: left;
  line-height: 1.4;
  padding-top: 15px;
  margin: 0 auto;
}

.primary-citation {
  font-size: 22px;
  line-height: 1.4;
  margin-top: 5px;
  text-align: justify;
  margin-left: 0px;
  font-family: "Helvetica", Times, Sans-serif;
}

.info-text {
  font-size: 22px;
  margin-top: 5px;
  /* Reduced margin-top */
  margin-left: 0px;
  text-align: justify;
  font-family: "Helvetica", Times, Sans-serif;
}

.sub-citation {
  margin-left: 20px;
  text-align: justify;
  font-family: "Helvetica", Times, Sans-serif;
}

.sub-title,
.sub-article {
  margin-left: 20px;
}



/* Colored TIPS letters */
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