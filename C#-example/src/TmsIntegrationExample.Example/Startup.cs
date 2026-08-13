// <copyright file="Startup.cs" company="Engaged Technologies">
//      Copyright (c) Engaged Technologies. All rights reserved.
//  </copyright>
// <summary>
//     Used to configure a JobHost
// </summary>

namespace TmsIntegrationExample.Example
{
    using Microsoft.AspNetCore.Builder;
    using Microsoft.AspNetCore.Hosting;
    using Microsoft.Extensions.Configuration;
    using Microsoft.Extensions.DependencyInjection;
    using Microsoft.Extensions.DependencyInjection.Extensions;
    using Microsoft.Extensions.Hosting;
    using TmsIntegrationExample.Services.Extensions;
    using TmsIntegrationExample.Services.MockApi;

    public class Startup
    {
        public IConfiguration Configuration { get; }

        public Startup(IConfiguration configuration)
        {
            this.Configuration = configuration;
        }

        public void ConfigureServices(IServiceCollection services)
        {
            services.AddSingleton<IConfiguration>(provider => Configuration);
            services.AddHostedService<TmsIntegrationExampleJob>();
            services.AddScoped<ITmsIntegrationExampleProcessor, TmsIntegrationExampleProcessor>();
            services.AddJsonSerializerOptions();
            services.AddHttpClient();
            services.AddTmsGatewayClient(this.Configuration.GetSection("Endpoints:TmsGatewayAPI"));
            services.AddAccessTokenClient(this.Configuration.GetSection("Endpoints:AccessTokenAPI"));
            services.TryAddScoped<IMockClient, MockClient>();
        }

        public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
        {
            var builder = new ConfigurationBuilder().AddEnvironmentVariables();

            if (env.IsDevelopment())
            {
                app.UseDeveloperExceptionPage();
                builder.AddUserSecrets<Startup>();
            }
            else
            {
                app.UseExceptionHandler("/Error");
            }
        }
    }
}
