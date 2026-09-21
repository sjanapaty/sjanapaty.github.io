---
layout: default
title: "Which geological periods does the world's oil come from?"
permalink: /projects/oil-basins/
---

<div class="row g-5 mb-5">
  <div class="col-md-12">

<h3 class="fw-bold mb-1">Which geological periods does the world's oil come from?</h3>
<p class="text-muted mb-4">An interactive map of global oil basins.</p>

<figure class="figure w-100 mb-4">
  <video id="oil-animation" class="figure-img img-fluid rounded w-100"
         autoplay muted playsinline style="cursor: pointer;"
         poster="{{ site.github.url }}/assets/img/projects/interval_present.png">
    <source src="{{ site.github.url }}/assets/img/projects/oil_history.mp4" type="video/mp4">
    <img src="{{ site.github.url }}/assets/img/projects/oil_history.gif"
         class="img-fluid rounded w-100"
         alt="Animated world map running from 460 million years ago to the present. Petroleum provinces appear as circles when their source rock was deposited and drift with the continents.">
  </video>
  <figcaption class="figure-caption mt-2">
    A clock runs from 460 million years ago to the present over reconstructed
    continents. Each circle is a petroleum province, placed where it sat when its
    source rock was deposited, then carried along as the plates move. Circle area
    is known oil in billion barrels. Colour is the source-rock interval, oldest
    darkest. The animation runs once and comes to rest on the present day. Click
    it to watch again, or
    <a href="{{ site.github.url }}/assets/img/projects/oil_history.gif">download the GIF</a>.
  </figcaption>
</figure>

<script>
  (function () {
    var v = document.getElementById('oil-animation');
    if (!v) { return; }
    v.addEventListener('click', function () {
      v.currentTime = 0;
      v.play();
    });
  })();
</script>

<p>Almost all of the oil we burn today came from organic matter buried during a
handful of narrow windows in Earth's history. Two thirds of it comes from just
two: the Upper Jurassic and the Middle Cretaceous.</p>

<table class="table table-sm w-auto">
  <thead>
    <tr><th>Source-rock interval</th><th class="text-end">Billion barrels</th></tr>
  </thead>
  <tbody>
    <tr><td>Silurian</td><td class="text-end">17</td></tr>
    <tr><td>Upper Devonian &ndash; Mississippian</td><td class="text-end">266</td></tr>
    <tr><td>Pennsylvanian &ndash; Lower Permian</td><td class="text-end">95</td></tr>
    <tr><td>Upper Jurassic</td><td class="text-end">866</td></tr>
    <tr><td>Middle Cretaceous</td><td class="text-end">977</td></tr>
    <tr><td>Oligocene &ndash; Miocene</td><td class="text-end">278</td></tr>
    <tr><td>All other intervals</td><td class="text-end">222</td></tr>
  </tbody>
</table>

<p>The positions are real reconstructions, not decoration. At 430 million years
ago the Arabian basins sit at roughly 40 degrees south on the northern margin of
Gondwana, which is exactly where the Qusaiba shale was laid down in a cold sea
after the end-Ordovician glaciation. That shale is the single largest source of
natural gas on Earth, but it barely registers for oil.</p>

<p>Volumes are known oil, meaning everything already produced plus what remains
in proved reserves. Province outlines come from the USGS World Petroleum
Assessment, which excluded the United States, so US basins and the
unconventional resources of Venezuela and Canada are estimated by hand. The
assignment of each basin to a source-rock interval is my own and is
approximate. Plate reconstructions use the model of Merdith and others (2021).</p>

<p class="text-muted"><em>An interactive version is in progress.</em></p>

  </div>
</div>
