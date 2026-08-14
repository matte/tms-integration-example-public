// <copyright file="Program.cs" company="Engaged Technologies">
//     Copyright (c) Engaged Technologies. All rights reserved.
// </copyright>
// <summary>
//     The main entry point
// </summary>

namespace TmsIntegrationExample.Example
{
    using Microsoft.AspNetCore.Hosting;
    using Microsoft.Extensions.Hosting;

    public static class Program
    {
        public static void Main(string[] args)
        {
            CreateHostBuilder(args).Build().Run();
        }

        public static IHostBuilder CreateHostBuilder(string[] args) =>
            Host.CreateDefaultBuilder(args)
                .ConfigureWebHostDefaults(webBuilder =>
                {
                    webBuilder.UseStartup<Startup>();
                });
    }
}
