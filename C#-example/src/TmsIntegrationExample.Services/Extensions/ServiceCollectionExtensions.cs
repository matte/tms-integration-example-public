// <copyright file="ServiceCollectionExtensions.cs" company="Engaged Technologies">
//      Copyright (c) Engaged Technologies. All rights reserved.
//  </copyright>
// <summary>
//     Extensions for IServiceCollection
// </summary>

namespace TmsIntegrationExample.Services.Extensions
{
    using System.Net.Http;
    using System.Text.Json;
    using System.Text.Json.Serialization;
    using Microsoft.Extensions.Configuration;
    using Microsoft.Extensions.DependencyInjection;
    using Microsoft.Extensions.DependencyInjection.Extensions;
    using TmsIntegrationExample.Services.TmsGatewayApi;
    using TmsIntegrationExample.Services.TmsGatewayApi.Configuration;
    using TmsIntegrationExample.Services.AccessToken.Configuration;
    using TmsIntegrationExample.Services.AccessToken;

    public static class ServiceCollectionExtensions
    {
        public static void AddTmsGatewayClient(this IServiceCollection services, IConfiguration config)
        {
            services.Configure<TmsGatewayConfiguration>(config);
            services.TryAddScoped<ITmsGatewayClient, TmsGatewayClient>();

            var configuration = config.Get<TmsGatewayConfiguration>();

            services.AddHttpClient(TmsGatewayClient.HttpClientName, client =>
            {
                client.BaseAddress = configuration.BaseAddress;
            });
        }

        public static void AddAccessTokenClient(this IServiceCollection services, IConfiguration config)
        {
            services.Configure<AccessTokenConfiguration>(config);
            services.TryAddSingleton<IAccessTokenClient, AccessTokenClient>();

            var configuration = config.Get<AccessTokenConfiguration>();

            services.AddHttpClient(AccessTokenClient.HttpClientName, client =>
            {
                client.BaseAddress = configuration.BaseAddress;
            })
            .ConfigurePrimaryHttpMessageHandler(() =>
            {
                return new HttpClientHandler()
                {
                    AllowAutoRedirect = false,
                };
            });
        }

        public static IServiceCollection AddJsonSerializerOptions(this IServiceCollection collection)
        {
            collection.TryAddSingleton(provider =>
            {
                var options = new JsonSerializerOptions
                {
                    Converters = { new JsonStringEnumConverter() },
                    DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
                    PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
                    WriteIndented = true,
                };

                return options;
            });

            return collection;
        }
    }
}
