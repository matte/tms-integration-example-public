// <copyright file="Startup.cs" company="Engaged Technologies">
//      Copyright (c) Engaged Technologies. All rights reserved.
//  </copyright>
// <summary>
//     Used to configure a JobHost
// </summary>

namespace TmsIntegrationExample.Example
{
    using Microsoft.Extensions.DependencyInjection;
    using Microsoft.Extensions.Hosting;
    using Microsoft.Extensions.Logging;
    using System;
    using System.Threading;
    using System.Threading.Tasks;

    public sealed class TmsIntegrationExampleJob : BackgroundService
    {
        private readonly IServiceProvider _serviceProvider;
        private readonly ILogger<TmsIntegrationExampleJob> _logger;

        public TmsIntegrationExampleJob(
            IServiceProvider serviceProvider,
            ILogger<TmsIntegrationExampleJob> logger)
        {
            _serviceProvider = serviceProvider;
            _logger = logger;
        }

        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
        {
            this._logger.LogInformation(
                $"{nameof(TmsIntegrationExampleJob)} is running.");

            await ExecuteJobAsync();
        }

        private async Task ExecuteJobAsync()
        {
            this._logger.LogInformation(
                $"{nameof(TmsIntegrationExampleJob)} is working.");

            using IServiceScope scope = this._serviceProvider.CreateScope();
            ITmsIntegrationExampleProcessor tmsIntegrationExampleProcessor = scope.ServiceProvider.GetRequiredService<ITmsIntegrationExampleProcessor>();

            Console.WriteLine($"Starting Job: {nameof(TmsIntegrationExampleJob)}");

            var numberProcessed = await tmsIntegrationExampleProcessor.ProcessAsync();

            Console.WriteLine($"Finished Job: {nameof(TmsIntegrationExampleJob)} Processed: {numberProcessed}");
        }

        public override async Task StopAsync(CancellationToken cancellationToken)
        {
            this._logger.LogInformation(
                $"{nameof(TmsIntegrationExampleJob)} is stopping.");

            await base.StopAsync(cancellationToken);
        }
    }
}
