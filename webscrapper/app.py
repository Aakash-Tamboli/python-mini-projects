from flask import Flask, render_template, request,jsonify;
from flask_cors import CORS,cross_origin;
import requests;
from bs4 import BeautifulSoup;
from urllib.request import urlopen;
import logging;
logging.basicConfig(filename="scrapper.log" , level=logging.INFO);

app = Flask(__name__);

@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html");

@app.route("/review" , methods = ['POST' , 'GET'])
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","");
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString;
            uClient = urlopen(flipkart_url);
            unstructuredFlipkartPage = uClient.read();
            uClient.close();
            structured_flipkart_html = BeautifulSoup(unstructuredFlipkartPage, "html.parser");
            product_divs = structured_flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"});
            del product_divs[0:3]; # reason to delete 0 to 3 is because in 0 to 3 header in there.
            product_div = product_divs[0];
            productLink = "https://www.flipkart.com" + product_div.div.div.div.a['href'];
            prodRes = requests.get(productLink)
            prodRes.encoding='utf-8'
            prod_html = BeautifulSoup(prodRes.text, "html.parser")
#            print(prod_html) # debug purpose
            commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})

            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            for commentbox in commentboxes:
                try:
                    #name.encode(encoding='utf-8')
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                except:
                    logging.info("name")

                try:
                    #rating.encode(encoding='utf-8')
                    rating = commentbox.div.div.div.div.text


                except:
                    rating = 'No Rating'
                    logging.info("rating")

                try:
                    #commentHead.encode(encoding='utf-8')
                    commentHead = commentbox.div.div.div.p.text

                except:
                    commentHead = 'No Comment Heading'
                    logging.info(commentHead)
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    #custComment.encode(encoding='utf-8')
                    custComment = comtag[0].div.text
                except Exception as e:
                    logging.info(e)

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)
            logging.info("log my final result {}".format(reviews))
            return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            logging.info(e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')


if __name__=="__main__":
    app.run(host="0.0.0.0")