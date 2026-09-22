---
layout: default
title: "Projects"
permalink: /projects/
---

<style>
  /* The footer's top border is the only rule on this page and it reads as a
     stray line under the listing, so hide it here. Other pages keep it. */
  footer.border-top { border-top: 0 !important; }
</style>

<div class="row g-5 mb-5">
  <div class="col-md-12">

<h4 class="fw-bold mt-4">Projects</h4>

{% for item in site.data.settings.projects %}
<div class="mt-3 mb-4">
  <h5 class="mb-1">
    <a href="{{ site.github.url }}{{ item.url }}">{{ item.name }}</a>
  </h5>
  <p class="mb-0 text-muted">{{ item.description }}</p>
</div>
{% endfor %}

  </div>
</div>
