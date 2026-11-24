---
layout: page
title: 기쁘띠콘 기술 블로그
---

안 쓰는 기프티콘을 이화인끼리 사고파는 중고 거래 마켓 **기쁘띠콘**을 만들며 배운 것을 정리한 팀 **오손도손**의 기술 블로그입니다.
Flask와 Firebase Realtime Database로 만들었고, 코드는 [GitHub 저장소](https://github.com/osp-5sondoson/2026_osp_project_5sondoson)에 있습니다.

{% assign slots = "Concept,Tip / Debugging,Guide,Explanation" | split: "," %}
{% for slot in slots %}
{% assign found = site.posts | where: "type", slot %}
<h2 class="post-type"><span class="chip">{{ slot }}</span></h2>
<ul class="post-cards">
{% for post in found reversed %}
  <li class="post-card">
    <a class="post-card__title" href="{{ post.url | relative_url }}">{{ post.title | escape }}</a>
    <div class="post-card__meta">{{ post.author }} · {{ post.date | date: "%Y.%m.%d" }}</div>
    {% if post.summary %}<p class="post-card__summary">{{ post.summary | escape }}</p>{% endif %}
  </li>
{% else %}
  <li class="post-card post-card--empty">작성 중</li>
{% endfor %}
</ul>
{% endfor %}
