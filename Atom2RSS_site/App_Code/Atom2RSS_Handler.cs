using System;
using System.Collections.Generic;
using System.Linq;
using System.ServiceModel.Syndication;
using System.Web;
using System.Xml;

namespace Atom2RSS
{

    /// <summary>
    /// Summary description for Atom2RSS_Handler
    /// </summary>
    public class Handler : IHttpHandler
    {

        public Handler()
        {
            //
            // TODO: Add constructor logic here
            //
        }

        // Override the ProcessRequest method. 
        public void ProcessRequest(HttpContext context)
        {
            var prog = context.Request.QueryString.Get("programid");
            var tracelevel = context.Request.QueryString.Get("tracelevel");

            var atom_url = "http://leifdev.leiflundgren.com:8091/py-cgi/sr_feed?" + context.Request.QueryString.ToString();
            // programid={0};tracelevel=9

            var reader = XmlReader.Create(atom_url);
            var feed = SyndicationFeed.Load(reader);

            var string_writer = new System.IO.StringWriter();

            //var out = context.Response.OutputStream
            feed.SaveAsRss20(XmlWriter.Create(string_writer, new XmlWriterSettings { Async=false, Indent=true, Encoding=System.Text.Encoding.UTF8 }));

            var rss = string_writer.ToString();

            context.Response.ContentType = "application/rss+xml; charset=utf-8";
            new System.IO.StreamWriter(context.Response.OutputStream).Write(rss);

            //context.Response.Write("<H1>This is an HttpHandler Test.</H1>");
            //context.Response.Write("<p>Your Browser:</p>");
            //context.Response.Write("Type: " + context.Request.Browser.Type + "<br>");
            //context.Response.Write("Version: " + context.Request.Browser.Version);
        }

        // Override the IsReusable property. 
        public bool IsReusable
        {
            get { return true; }
        }
    }
}