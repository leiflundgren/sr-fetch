using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;

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
            context.Response.Write("<H1>This is an HttpHandler Test.</H1>");
            context.Response.Write("<p>Your Browser:</p>");
            context.Response.Write("Type: " + context.Request.Browser.Type + "<br>");
            context.Response.Write("Version: " + context.Request.Browser.Version);
        }

        // Override the IsReusable property. 
        public bool IsReusable
        {
            get { return true; }
        }
    }
}