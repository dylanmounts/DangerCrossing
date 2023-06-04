# dangercrossing
<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![LinkedIn][linkedin-shield]][linkedin-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://dangercrossing.com">
    <img src="https://github.com/dylanmounts/dangercrossing/blob/main/services/web/danger_crossing/danger_crossing/static/img/favicon-180x180.png" alt="Logo" width="90" height="90">
  </a>

<h3 align="center">Danger Crossing</h3>

  <p align="center">
    Traffic accident heatmap reflecting accidents reported by the Missouri State Highway Patrol.
    <br />
    <a href="https://dangercrossing.com"><strong>https://dangercrossing.com</strong></a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
        <li><a href="#services">Services</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About

[![Danger Crossing Screen Shot][product-screenshot]](https://dangercrossing.com)

The Missouri State Highway Patrol (MSHP) publishes their [accidents reports](https://www.mshp.dps.missouri.gov/HP68/search.jsp) online. Most of these reports contain the longitude and latitude coordinates of the accident. This project gathers accident information from the MSHP's website and displays it on an interactive heatmap which can be viewed in the user's browser.

The project is comprised of several Docker containers which serve [distinct purposes](#services). Docker Compose is used to coordinate these containers into a single application.

<p align="right">(<a href="#top">back to top</a>)</p>



### Built With

* [Python](https://www.python.org)
* [Flask](https://flask.palletsprojects.com)
* [Bootstrap](https://getbootstrap.com)
* [Docker](https://www.docker.com)

### Services
The project is comprised of four separate Docker containers which serve distinct purposes. Docker Compose coordinates these containers into a single application.

#### Web

The Flask application responsible for rendering the heatmap and governing the user's interactions with it. In development builds, also acts as the web server.

#### Cron

A crontab which runs the `danger_maker.py` script at some predetermined interval (currently set to once every 3 hours). The `danger_maker.py` script is responsible for gathering and saving new accidents from the MSHP's website.

### Redis

A caching server to store and retrieve the dictionary of accident information.

#### Nginx

The web server used in production builds.

#### Tile Server

An OpenStreetMap PNG tile server built using [Overv's openstreetmap-tile-server](https://github.com/Overv/openstreetmap-tile-server/) Docker project. Relies on the `missouri_et_al.osm.pbf` extract file provided by [Protomaps](https://protomaps.com/downloads/osm).

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple example steps.

### Prerequisites

1. Install [Git LFS](https://git-lfs.com/)
2. Install [Docker](https://docs.docker.com/get-docker/)
3. Install [Docker Compose](https://docs.docker.com/compose/install/)

### Installation

1. Clone the repo
    ```sh
    git clone https://github.com/dylanmounts/dangercrossing.git
    ```
2. Navigate to the repo directory
    ```sh
    cd dangercrossing
    ```
3. Verify the PBF extract was downloaded
   ```sh
   git lfs pull
   ```
4. Build and start the project
   1. In a development environment
      ```sh
      docker compose -f docker-compose.dev.yml up --build -d
      ```
   2. In a production environment
      ```sh
      docker compose up --build -d
      ```
5. **(Optional)** Add initial accidents to the map manually (or wait for the Cron service to pull new accidents every three hours)
   ```sh
   docker compose exec cron python danger_maker.py
   ```

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Dylan Mounts - dmounts@gmail.com

Project Link: [https://github.com/dylanmounts/dangercrossing](https://github.com/dylanmounts/dangercrossing)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [Missouri State Highway Patrol](https://www.mshp.dps.missouri.gov/HP68/search.jsp) for making this information freely and easily accessible. Additional thanks for including longitude and latitude coordinates in their accident reports.
* [OpenLayers](https://openlayers.org/) and their contributors for providing the map data.
* [Protomaps](https://protomaps.com/downloads/osm) for providing the Missouri PBF extract.
* [Overv's openstreetmap-tile-server](https://github.com/Overv/openstreetmap-tile-server/) for maintaining the tile server Docker project.
* [othneildrew's Best-README-Template](https://github.com/othneildrew/Best-README-Template.git) for this README template.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/dylan-mounts
[product-logo]: https://github.com/dylanmounts/dangercrossing/blob/main/services/web/danger_crossing/danger_crossing/static/img/favicon-180x180.png
[product-screenshot]: https://github.com/dylanmounts/dangercrossing/blob/main/services/web/danger_crossing/danger_crossing/static/img/danger_crossing_heatmap_thumb.png