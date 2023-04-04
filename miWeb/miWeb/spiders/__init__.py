import scrapy
import urllib

from scrapy_splash import SplashRequest


class MiAraña(scrapy.Spider):
    name = "mi_araña"
    start_urls = ["https://www.classcentral.com/"]

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(
                url, self.parse, endpoint="render.html", args={"wait": 15}
            )

    def parse(self, response):
        html = response.body

        # Save HTML in page.html file
        with open("page.html", "wb") as f:
            f.write(html)

        # Hacemos una nueva solicitud a Splash para obtener el CSS después de que la página haya cargado
        yield SplashRequest(
            response.url,
            self.parse_css,
            endpoint="execute",
            args={
                "lua_source": """
                                function main(splash, args)
                                    splash:go(args.url)
                                    splash:wait(15)
                                    return {
                                        css = splash:select('style'):text(),
                                    }
                                end
                            """
            },
        )

    def parse_css(self, response):
        css = response.data["css"]

        # Guardar CSS en un archivo
        with open("estilos.css", "w") as f:
            f.write(css)

        # Descargar imágenes y otros recursos
        assets_folder = "assets/resources"
        for image in response.css("img"):
            url = image.attrib["src"]
            filename = url.split("/images")[-1]
            urllib.request.urlretrieve(url, assets_folder + filename)
        for link in response.css('link[rel="icon"]'):
            url = link.attrib["href"]
            filename = url.split("/links")[-1]
            urllib.request.urlretrieve(url, assets_folder + filename)

        print(css)
